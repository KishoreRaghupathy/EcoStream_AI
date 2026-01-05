import os
import re
import time
import logging
from typing import List, Optional
import pandas as pd
from sqlalchemy import create_engine, text
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser

from src.chat.models import ChatRequest, ChatResponse
from src.chat.prompts import SYSTEM_PROMPT, EXPLANATION_PROMPT
from src.chat.safety import SQLValidator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_URL = os.getenv('AIRFLOW__DATABASE__SQL_ALCHEMY_CONN', 'postgresql+psycopg2://ecostream:ecostream@localhost:5432/ecostream_db')

class ChatService:
    def __init__(self):
        self.engine = create_engine(DB_URL)
        self.llm = ChatOllama(model="llama3", temperature=0) # Or mistral
        self.sql_parser = StrOutputParser()
        self._setup_db()

    def _setup_db(self):
        """Create chat_logs table if not exists"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS public.chat_logs (
                    id SERIAL PRIMARY KEY,
                    question TEXT,
                    generated_sql TEXT,
                    llm_response TEXT,
                    execution_time_ms FLOAT,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """))
            conn.commit()

    def _extract_sql(self, llm_output: str) -> str:
        """Extract SQL from markdown code block"""
        match = re.search(r'```sql\n(.*?)\n```', llm_output, re.DOTALL)
        if match:
            return match.group(1).strip()
        # Fallback: if no code block, assume entire text is SQL if it starts with SELECT
        if llm_output.strip().upper().startswith('SELECT'):
            return llm_output.strip()
        return ""

    def _identify_tables(self, sql: str) -> List[str]:
        tables = []
        if 'silver.fact_air_quality' in sql: tables.append('fact_air_quality')
        if 'silver.fact_weather' in sql: tables.append('fact_weather')
        if 'gold.pm25_predictions' in sql: tables.append('pm25_predictions')
        return tables

    def ask(self, request: ChatRequest) -> ChatResponse:
        start_time = time.time()
        
        # 1. Generate SQL
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=request.question)
        ]
        
        try:
            raw_llm_response = self.llm.invoke(messages)
            generated_sql = self._extract_sql(raw_llm_response.content)
            
            if not generated_sql:
                raise ValueError("Could not generate valid SQL")

            # 2. Validate SQL
            if not SQLValidator.validate(generated_sql):
                raise ValueError(f"Unsafe SQL detected: {generated_sql}")
            
            # 3. Execute SQL
            df = pd.read_sql(text(generated_sql), self.engine)
            result_str = df.to_markdown() if not df.empty else "No results found."

            # 4. Generate Explanation
            explain_prompt = EXPLANATION_PROMPT.format(
                question=request.question,
                query=generated_sql,
                result=result_str
            )
            explanation = self.llm.invoke([HumanMessage(content=explain_prompt)]).content
            
            execution_time = (time.time() - start_time) * 1000
            
            # 5. Log
            self._log_interaction(request.question, generated_sql, explanation, execution_time)
            
            return ChatResponse(
                answer=explanation,
                data_used=self._identify_tables(generated_sql),
                confidence="high" if not df.empty else "low",
                sql_generated=generated_sql,
                execution_time_ms=execution_time
            )

        except Exception as e:
            logger.error(f"Error processing chat: {e}")
            return ChatResponse(
                answer=f"I encountered an error analyzing your request: {str(e)}",
                data_used=[],
                confidence="low",
                execution_time_ms=(time.time() - start_time) * 1000
            )

    def _log_interaction(self, question, sql, response, duration):
        try:
            with self.engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO public.chat_logs (question, generated_sql, llm_response, execution_time_ms)
                    VALUES (:q, :sql, :resp, :time)
                """), {"q": question, "sql": sql, "resp": response, "time": duration})
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to log chat interaction: {e}")

chat_service = ChatService()

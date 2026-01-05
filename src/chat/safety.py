import re

class SQLValidator:
    FORBIDDEN_KEYWORDS = [
        r'\bDROP\b', r'\bDELETE\b', r'\bINSERT\b', r'\bUPDATE\b', 
        r'\bALTER\b', r'\bGRANT\b', r'\bTRUNCATE\b', r'\bEXEC\b', 
        r'\bCREATE\b', r'\bREPLACE\b'
    ]

    @staticmethod
    def validate(sql: str) -> bool:
        """
        Validates the SQL query against a strict allow-list and deny-list.
        Returns True if safe, False otherwise.
        """
        # 1. Normalize
        sql_upper = sql.upper().strip()

        # 2. Must start with SELECT or WITH
        if not (sql_upper.startswith('SELECT') or sql_upper.startswith('WITH')):
            return False

        # 3. Check forbidden keywords
        for pattern in SQLValidator.FORBIDDEN_KEYWORDS:
            if re.search(pattern, sql_upper):
                return False

        # 4. Check for multiple statements (semicolon hacks)
        # We allow semicolons inside quotes, but simpler check: 
        # sql should rarely have semicolon in middle for RAG. 
        # Let's count semicolons that are not inside quotes? 
        # For simplicity, let's just checking if there is more than 1 semicolon at end.
        cleaned = sql_upper.replace(";", "")
        if len(sql_upper) - len(cleaned) > 1:
            # More than one semicolon is suspicious
            return False
            
        return True

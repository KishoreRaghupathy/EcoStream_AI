import numpy as np
import logging
from typing import Dict, Any, List
from scipy import stats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DriftDetector:
    def __init__(self, reference_data: np.ndarray = None):
        self.reference_data = reference_data
        
    def set_reference(self, data: np.ndarray):
        """Set key statistical properties of reference data (e.g. training set)"""
        self.reference_data = data
        
    def check_drift(self, current_data: np.ndarray, threshold: float = 0.05) -> Dict[str, Any]:
        """
        Check for drift using KS Test.
        Returns dictionary with is_drift boolean and p_value.
        """
        if self.reference_data is None:
            logger.warning("No reference data set for drift detection")
            return {"is_drift": False, "reason": "No reference data"}
            
        # Kolmogorov-Smirnov Test
        # Null hypothesis: the two distributions are identical.
        # If p_value < threshold, reject null hypothesis -> DRIFT DETECTED.
        statistic, p_value = stats.ks_2samp(self.reference_data, current_data)
        
        is_drift = p_value < threshold
        
        if is_drift:
            logger.warning(f"Drift detected! p_value={p_value:.5f} < threshold={threshold}")
            
        return {
            "is_drift": is_drift,
            "p_value": p_value,
            "statistic": statistic
        }

    def check_mean_shift(self, current_data: np.ndarray, std_dev_threshold: float = 2.0) -> Dict[str, Any]:
        """
        Simple mean shift check.
        """
        if self.reference_data is None:
             return {"is_drift": False, "reason": "No reference data"}
             
        ref_mean = np.mean(self.reference_data)
        ref_std = np.std(self.reference_data)
        
        curr_mean = np.mean(current_data)
        
        z_score = abs(curr_mean - ref_mean) / (ref_std + 1e-9) # Avoid div by zero
        
        is_drift = z_score > std_dev_threshold
        
        if is_drift:
             logger.warning(f"Mean shift drift detected! Z-score={z_score:.2f}")
             
        return {
            "is_drift": is_drift,
            "z_score": z_score,
            "current_mean": curr_mean,
            "reference_mean": ref_mean
        }

if __name__ == "__main__":
    # Test run
    # Generate reference data
    ref = np.random.normal(0, 1, 1000)
    
    # Generate same distribution
    curr_same = np.random.normal(0, 1, 100)
    
    # Generate drifted distribution
    curr_drift = np.random.normal(0.5, 1.2, 100)
    
    detector = DriftDetector()
    detector.set_reference(ref)
    
    print("Testing same distribution:")
    print(detector.check_drift(curr_same))
    
    print("\nTesting drifted distribution:")
    print(detector.check_drift(curr_drift))

import pandas as pd
import logging

logger = logging.getLogger(__name__)

def optimize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Optimizes a pandas DataFrame to reduce memory usage.
    Converts object columns to category and downcasts numeric types.
    """
    if df.empty:
        return df

    original_size = df.memory_usage(deep=True).sum()
    
    # Optimize objects to category
    for col in df.select_dtypes(include=['object']):
        if df[col].nunique() / len(df) < 0.5:
            df[col] = df[col].astype('category')
            
    # Optimize integers
    for col in df.select_dtypes(include=['int64']):
        col_min, col_max = df[col].min(), df[col].max()
        if col_min >= -128 and col_max <= 127:
            df[col] = df[col].astype('int8')
        elif col_min >= -32768 and col_max <= 32767:
            df[col] = df[col].astype('int16')
        elif col_min >= -2147483648 and col_max <= 2147483647:
            df[col] = df[col].astype('int32')
            
    # Optimize floats
    for col in df.select_dtypes(include=['float64']):
        df[col] = pd.to_numeric(df[col], downcast='float')
        
    optimized_size = df.memory_usage(deep=True).sum()
    reduction = (1 - optimized_size / original_size) * 100 if original_size > 0 else 0
    
    logger.debug(f"DataFrame optimized: {reduction:.1f}% memory reduction")
    return df

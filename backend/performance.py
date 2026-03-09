# TEAM: Backend Infrastructure
# Performance monitoring utilities
# Provides decorators and utilities for tracking performance metrics

import time
import logging
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger(__name__)


def monitor_performance(operation_name: str, threshold_ms: float = None):
    """
    Decorator to monitor performance of async functions
    
    Args:
        operation_name: Name of the operation being monitored
        threshold_ms: Optional threshold in milliseconds. If exceeded, log a warning
    
    Usage:
        @monitor_performance("database_query", threshold_ms=500)
        async def get_session(session_id: str):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                elapsed_ms = (time.time() - start_time) * 1000
                
                # Log performance
                if threshold_ms and elapsed_ms > threshold_ms:
                    logger.warning(
                        f"⚠️  Performance: {operation_name} took {elapsed_ms:.2f}ms "
                        f"(threshold: {threshold_ms}ms)"
                    )
                else:
                    logger.debug(f"⏱️  Performance: {operation_name} took {elapsed_ms:.2f}ms")
                
                return result
                
            except Exception as e:
                elapsed_ms = (time.time() - start_time) * 1000
                logger.error(
                    f"❌ Performance: {operation_name} failed after {elapsed_ms:.2f}ms - {e}"
                )
                raise
        
        return wrapper
    return decorator


def monitor_sync_performance(operation_name: str, threshold_ms: float = None):
    """
    Decorator to monitor performance of synchronous functions
    
    Args:
        operation_name: Name of the operation being monitored
        threshold_ms: Optional threshold in milliseconds. If exceeded, log a warning
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                elapsed_ms = (time.time() - start_time) * 1000
                
                # Log performance
                if threshold_ms and elapsed_ms > threshold_ms:
                    logger.warning(
                        f"⚠️  Performance: {operation_name} took {elapsed_ms:.2f}ms "
                        f"(threshold: {threshold_ms}ms)"
                    )
                else:
                    logger.debug(f"⏱️  Performance: {operation_name} took {elapsed_ms:.2f}ms")
                
                return result
                
            except Exception as e:
                elapsed_ms = (time.time() - start_time) * 1000
                logger.error(
                    f"❌ Performance: {operation_name} failed after {elapsed_ms:.2f}ms - {e}"
                )
                raise
        
        return wrapper
    return decorator


class PerformanceTimer:
    """Context manager for timing code blocks"""
    
    def __init__(self, operation_name: str, threshold_ms: float = None):
        self.operation_name = operation_name
        self.threshold_ms = threshold_ms
        self.start_time = None
        self.elapsed_ms = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed_ms = (time.time() - self.start_time) * 1000
        
        if exc_type is None:
            # Success
            if self.threshold_ms and self.elapsed_ms > self.threshold_ms:
                logger.warning(
                    f"⚠️  Performance: {self.operation_name} took {self.elapsed_ms:.2f}ms "
                    f"(threshold: {self.threshold_ms}ms)"
                )
            else:
                logger.debug(f"⏱️  Performance: {self.operation_name} took {self.elapsed_ms:.2f}ms")
        else:
            # Error
            logger.error(
                f"❌ Performance: {self.operation_name} failed after {self.elapsed_ms:.2f}ms"
            )
        
        return False  # Don't suppress exceptions

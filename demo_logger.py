#!/usr/bin/env python3
"""
Demo script showcasing the new professional logging system for Causal-Copilot
Run this to see the improved command-line output formatting
"""

import time
import numpy as np
from utils.logger import logger, set_log_level, LogLevel

def main():
    """Demo the logging system with simulated causal analysis workflow"""
    
    # Set the appropriate log level (INFO for normal operation)
    set_log_level(LogLevel.INFO)
    
    # Start the session
    logger.header("Causal-Copilot Analysis Demo")
    
    # Simulate data loading
    logger.data("Loading sample dataset: sachs.csv")
    time.sleep(0.3)
    
    # Show detailed data information
    data_details = {
        "Shape": "(7466, 11)",
        "Columns": 11,
        "Missing values": 0,
        "Data type": "Continuous"
    }
    logger.data_info("Dataset loaded", data_details)
    
    # Simulate preprocessing
    logger.section("Data Preprocessing")
    logger.detail("Checking data quality and variable types")
    time.sleep(0.2)
    logger.detail("Handling missing values and outliers")
    time.sleep(0.2)
    logger.success("Preprocessing completed")
    
    # Simulate algorithm selection
    logger.section("Algorithm Selection")
    
    logger.step(1, 3, "Filtering suitable algorithms")
    time.sleep(0.2)
    logger.detail("Filtered to 8 candidate algorithms")
    
    logger.step(2, 3, "Ranking algorithms by suitability")
    time.sleep(0.2)
    logger.detail("Algorithm ranking completed")
    
    logger.step(3, 3, "Optimizing hyperparameters")
    time.sleep(0.2)
    logger.algorithm("Selected algorithm", "PC Algorithm")
    logger.detail("Hyperparameters: 3 parameters optimized")
    
    # Simulate algorithm execution with progress
    logger.section("Algorithm Execution")
    logger.process("Running PC Algorithm")
    for i in range(0, 101, 25):
        time.sleep(0.15)
        logger.progress(i, 100, "Running PC Algorithm")
    
    logger.detail("Discovered 15 edges in causal graph")
    logger.checkpoint("Causal discovery completed")
    
    # Simulate evaluation
    logger.section("Graph Evaluation")
    logger.detail("Comparing with ground truth graph")
    time.sleep(0.2)
    
    # Show evaluation metrics
    metrics = {
        "Structural Hamming Distance": 8.0,
        "Precision": 0.8571,
        "Recall": 0.7500,
        "F1-Score": 0.8000,
        "Execution Time": "2.34s"
    }
    logger.metrics_table(metrics, "Performance Metrics")
    
    # Simulate post-processing
    logger.section("Graph Refinement")
    logger.detail("Applying bootstrap sampling and statistical tests")
    time.sleep(0.3)
    logger.success("Graph refinement completed")
    
    # Simulate report generation
    logger.section("Report Generation")
    
    logger.step(1, 3, "Analyzing causal relationships")
    time.sleep(0.2)
    logger.detail("Causal relationship analysis completed")
    
    logger.step(2, 3, "Generating comprehensive report")
    time.sleep(0.3)
    
    logger.step(3, 3, "Report saved successfully")
    logger.detail("Report location: analysis_report.pdf")
    
    # Final checkpoint
    logger.checkpoint("Analysis session completed")
    logger.elapsed_time("Total analysis time")
    
    # Show different log levels
    print("\n" + "="*60)
    print("DEMONSTRATING DIFFERENT LOG LEVELS:")
    print("="*60)
    
    logger.info("This is an info message (normal operation)")
    logger.success("This is a success message (completed tasks)")
    logger.save("File saved successfully", "analysis_report.pdf")
    logger.warning("This is a warning message (non-critical issues)")
    logger.error("This is an error message (recoverable errors)")
    logger.debug("This is a debug message (detailed technical info)")
    
    # Show what happens in quiet mode
    print("\n" + "="*60)
    print("QUIET MODE (only warnings and errors):")
    print("="*60)
    
    set_log_level(LogLevel.WARNING)
    logger.info("This info message won't show in quiet mode")
    logger.success("This success message won't show either")
    logger.warning("But this warning will show")
    logger.error("And this error will show")

if __name__ == "__main__":
    main()
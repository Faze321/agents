#!/usr/bin/env python
import sys
import warnings
import os

# 禁用遥测，避免远程连接超时错误
os.environ['OTEL_SDK_DISABLED'] = 'true'

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

from coder.crew import Coder


# Create output directory if it doesn't exist
os.makedirs('output', exist_ok=True)

assignment = 'Write a python program to calculate the first 10,000 terms \
    of this series, multiplying the total by 4: 1 - 1/3 + 1/5 - 1/7 + ...'

def run():
    """
    Run the crew.
    """
    inputs = {
        'assignment': assignment,
    }
    
    result = Coder().crew().kickoff(inputs=inputs)
    print(result.raw)

if __name__ == "__main__":
    run()
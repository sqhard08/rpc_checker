# RPC Checker

This script automates the process of monitoring and switching between different RPC (Remote Procedure Call) endpoints to ensure the highest availability and performance for blockchain interactions.

## Key Features
- **Periodic RPC Monitoring**: Regularly checks the latency and availability of specified RPC URLs.
- **Automatic Fallback**: Automatically switches to the best available alternative if the current RPC becomes unavailable.
- **Configurable Settings**: Manages the current RPC URL using a configuration file, which is updated when a better RPC is found.
- **Logging**: Logs all activities, including RPC checks, updates, and errors, providing a clear audit trail.
- **Shell Command Execution**: Executes shell commands to restart services after updating the RPC endpoint.
- **Concurrent RPC Checks**: Utilizes multithreading to check multiple RPC endpoints concurrently, improving efficiency.

## Highlights
- **Resilience**: Ensures continuous operation by automatically switching to a functioning RPC endpoint when the current one fails.
- **Detailed Logs**: Maintains detailed logs in `rpc_checker.log` for monitoring and debugging purposes.
- **Customizable Intervals**: Allows customization of the check interval to suit different environments and requirements.
- **Integrated Shell Commands**: Automates the process of restarting services after an RPC switch, ensuring seamless transitions.

## Installation

To install and use this RPC checker, follow these steps:

1. **Clone the Repository**:
    ```sh
    git clone https://github.com/yourusername/rpc_checker.git
    ```
2. **Navigate to the Project Directory**:
    ```sh
    cd rpc_checker
    ```
3. **Place the Script and Configuration File**:
    - Ensure the `rpc_checker.py` script and the `config.json` file (or any other required configuration files) are placed in the project directory.
    
4. **Install Required Dependencies**:
    ```sh
    pip install requests
    ```
5. **Configure the Script**:
    - Edit the `config.json` file to include the appropriate configuration settings, such as the initial RPC URL and wallet settings.

6. **Run the Script**:
    ```sh
    python rpc_checker.py
    ```

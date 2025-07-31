import sys
import asyncio
import os
from multiprocessing import Process
import uvicorn
import json # For parsing JSONResponse
import traceback # For logging tracebacks

from dotenv import load_dotenv
load_dotenv() # Load environment variables for this process

# Import necessary components from main.py
# Assuming logger, app, make_outgoing_call, and PORT are exposed at the top level
from main import logger, app, make_outgoing_call, PORT

def run_fastapi_app_process():
    """Function to run the FastAPI app in a separate process."""
    logger.info("Starting FastAPI app in a separate process (uvicorn.run)...")
    try:
        # uvicorn.run is blocking, so it should be the last call in this function
        uvicorn.run(app, host="0.0.0.0", port=PORT)
    except Exception as e:
        logger.error(f"FastAPI app process failed to start: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")

async def initiate_outgoing_call(target_phone_number: str):
    """Initiates an outgoing call after the FastAPI app has started."""
    logger.info(f"Waiting 5 seconds for the FastAPI app to start...")
    await asyncio.sleep(5) # Give the server some time to start up

    logger.info(f"Attempting to initiate outgoing call to: {target_phone_number}")
    try:
        # Call the make_outgoing_call function directly
        # The 'from_number' argument will use the default from main.py's definition
        # which pulls from TWILIO_PHONE_NUMBER env var.
        response = await make_outgoing_call(to_number=target_phone_number)
        
        # FastAPI's JSONResponse has a .body attribute which is bytes
        response_content = response.body.decode('utf-8')
        
        # Log the raw response content first for debugging
        logger.debug(f"Raw call initiation response: {response_content}")

        # Attempt to parse the JSON response
        response_json = json.loads(response_content)
        
        if response.status_code == 200:
            logger.info(f"[bold green]Outgoing call initiated successfully. Call SID: {response_json.get('call_sid')}[/bold green]")
        else:
            logger.error(f"[bold red]Failed to initiate call. Status Code: {response.status_code}, Detail: {response_json.get('detail', 'N/A')}, Error: {response_json.get('error', 'N/A')}[/bold red]")

    except json.JSONDecodeError as e:
        logger.error(f"[bold red]Failed to decode JSON response from make_outgoing_call: {e}[/bold red]")
        logger.error(f"[bold red]Response content was: {response_content}[/bold red]")
    except Exception as e:
        logger.error(f"[bold red]An unexpected error occurred during call initiation: {e}[/bold red]")
        logger.error(f"[bold red]Traceback: {traceback.format_exc()}[/bold red]")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        logger.error("[bold red]Usage: python call_outgoing.py <phone_number>[/bold red]")
        sys.exit(1)

    phone_number_to_call = sys.argv[1]

    # Start the FastAPI app in a separate process
    fastapi_process = Process(target=run_fastapi_app_process)
    fastapi_process.start()

    async def main_async():
        try:
            # Run the async function to initiate the call
            await initiate_outgoing_call(phone_number_to_call)
            
            # After initiating the call, keep the main process alive
            # This allows the FastAPI process to continue running and handle the call
            logger.info("[bold yellow]Outgoing call initiated. Press Ctrl+C to terminate the script and hang up.[/bold yellow]")
            while True:
                await asyncio.sleep(1) # Keep the main thread busy without consuming CPU
                
        except KeyboardInterrupt:
            logger.info("[bold yellow]Outgoing call script interrupted by user.[/bold yellow]")
        finally:
            if fastapi_process.is_alive():
                logger.info("Terminating FastAPI app process...")
                fastapi_process.terminate()
                fastapi_process.join()
                logger.info("FastAPI app process terminated.")

    asyncio.run(main_async()) 
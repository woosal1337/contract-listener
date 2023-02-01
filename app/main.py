import json
import os
import time

from loguru import logger
from web3 import Web3


class Listener:
    def __init__(self):
        try:
            if os.path.exists("config.json"):
                logger.info("Config file found, loading config.json...")

                with open("config.json") as f:
                    self.config = json.load(f)
                    logger.info("Config loaded, checking for required parameters...")

                for parameter in ["contract_address", "abi", "rpc_url"]:
                    if parameter not in self.config.keys():
                        logger.error(f"Parameter {parameter} not found in config.json")
                        self.config[parameter] = self.set_config_parameter(parameter)

                    else:
                        if self.config[parameter] == "":
                            logger.error(f"Parameter {parameter} is empty!")
                            self.config[parameter] = self.set_config_parameter(
                                parameter
                            )

                json.dump(self.config, open("config.json", "w"))
                logger.info("Config loaded successfully, starting listener...")

            else:
                logger.info("Config file not found, creating config.json...")
                with open("config.json", "w+") as f:
                    f.write("{}")

                self.config = self.setup_config()

            self.w3 = Web3(Web3.HTTPProvider(self.config["rpc_url"]))

            self.contract = self.w3.eth.contract(
                address=self.config["contract_address"],
                abi=self.config["abi"],
            )

            self.events = self.get_listeners()

        except Exception as e:
            logger.error(f"Error while loading config: {e}")
            exit(1)

    @staticmethod
    def set_config_parameter(parameter: str) -> dict:
        try:
            current_missing_parameter = input(
                f"Please enter the value for {parameter}: "
            )

            while current_missing_parameter == "":
                print("Missing input, please try again!")
                current_missing_parameter = input(
                    f"Please enter the value for {parameter}: "
                )

            if parameter == "abi":
                current_missing_parameter = json.loads(current_missing_parameter)

            return current_missing_parameter

        except Exception as e:
            logger.error(f"Error while setting config parameter: {e}")
            exit(1)

    def get_listeners(self):
        try:
            events = [
                i
                for i in self.contract.events.__dict__.keys()
                if i[0] != "_" and i != "abi"
            ]

            logger.info(f"Found {events} [{len(events)}] events to listen " f"for.")

            return events

        except Exception as e:
            logger.error(f"Error while listening for event: {e}")
            exit(1)

    def listen(self, listener_name: str):
        try:
            event_filter = self.contract.events[listener_name].createFilter(
                fromBlock="latest"
            )

            while True:
                try:
                    for event in event_filter.get_new_entries():
                        logger.info(f"New event found: {event}")
                        # do_something()

                    time.sleep(1)

                except Exception as e:
                    logger.error(f"Error while listening for event: {e}")
                    time.sleep(1)

        except Exception as e:
            logger.error(f"Error while listening for event: {e}")
            logger.error(e)
            exit(1)


if __name__ == "__main__":
    listener = Listener()
    listener.listen("Transfer")

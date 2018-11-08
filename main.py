import slack_handlers

import time

RTM_READ_DELAY = 1 # 1 second delay between reading from RTM


def main():
    slack_handlers.setup()
    while True:
        command, channel = slack_handlers.parse_bot_commands(slack_client.rtm_read())
        if command:
            slack_handlers.handle_command(command, channel)
        time.sleep(RTM_READ_DELAY)

if __name__ == "__main__":
    main()

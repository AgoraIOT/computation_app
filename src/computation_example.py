import math
import time

from agoraiot import config, IoDataReportMsg, logger, bus_client, IoPoint, AgoraTimeStamp

class ComputationExample:
    def __init__(self):
        self.message_count = 0

        self.factor = float(config['AppConfig']['Factor'])

        self.input1 = config['AppConfig']['Input1']
        self.input2 = config['AppConfig']['Input2']

        self.output1 = config['AppConfig']['Output1']
        self.output2 = config['AppConfig']['Output2']

    async def run(self):
        logger.info("app name: " + str(config["Name"]))
        bus_client.connect(30)
        time.sleep(1)

        # handle messages as they arrive...
        while bus_client.is_connected():
            for msg in bus_client.messages.get_data_messages():
                self.agora_message_handler(msg)
            for msg in bus_client.messages.get_request_messages():
                self.agora_message_handler(msg)
            for msg in bus_client.messages.get_application_messages():
                self.agora_message_handler(msg)

            time.sleep(1)
        logger.info("Exit name: " + str(config["Name"]))
        

    def agora_message_handler(self, msg: IoDataReportMsg):
        logger.info('Message received of type - {}'.format(msg.header.MessageType))
        self.message_count += 1

        if msg.header.MessageType != 'IODataReport':
            logger.info('Not a valid data report. Skipping message!')
            return


        logger.debug('Devices in message to process: {}'.format(len(msg.device)))
        print('Processing Message {id} with timestamp {epoch}. Count={cnt}'.format(id=msg.header.MessageID, epoch=msg.header.TimeStamp,cnt=len(msg.device)))

        output_report = IoDataReportMsg()
        # output_report.header = msg.header
        output_report.header.TimeStamp = AgoraTimeStamp()
        output_report.device = []

        for curr_device in msg.device:
            self.process_device(curr_device, output_report)

        if len(output_report.device) > 0:
            print('Sending data report out')
            bus_client.send_data(output_report)
        else:
            print('Empty device data ?!? Not sending data report out')

    def process_device(self, curr_device, output_report):
        print('Device ID = {id}, tag count = {cnt}'.format(id=curr_device.id, cnt=len(curr_device.tags)))

        # read input data
        input1 = curr_device.tags.get(self.input1, None)
        input2 = curr_device.tags.get(self.input2, None)

        if input1 is None or input2 is None:
            logger.error("Missing tags for calculation. Values seen: {}".format(curr_device.tags))
            return

        # calculate velocities based on input
        average    = self.factor * (input1.value + input2.value) / 2
        difference = self.factor * (input1.value - input2.value)

        logger.info("input[i1:{}, i2:{}] ---> output[o1:{}, o2:{}]".format(
                    input1.value, input2.value,
                    average, difference))

        # generate output tags
        o1_io = IoPoint(average   , quality_code=0, timestamp=AgoraTimeStamp())
        o2_io = IoPoint(difference, quality_code=0, timestamp=AgoraTimeStamp())

        output_report.add_device_data(curr_device.id, self.output1, o1_io)
        output_report.add_device_data(curr_device.id, self.output2, o2_io)

        print('# of processed messages: {cnt}'.format(cnt=self.message_count))

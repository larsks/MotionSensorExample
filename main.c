#include <unistd.h>
#include <stdio.h>
#include <math.h>
#include <time.h>
#include <zmq.h>
#include <string.h>
#include <msgpack.h>

#include "MotionSensor.h"

#define delay_ms(a) usleep(a*1000)

void free_old_buffer(void *data, void *buffer) {
	msgpack_sbuffer_destroy((msgpack_sbuffer *)buffer);
}

int main() {
	void *ctx = zmq_init(1);
	void *pub = zmq_socket(ctx, ZMQ_PUB);
	zmq_msg_t msg;
	int rc;

	zmq_bind(pub, "tcp://*:8000");

	ms_open();
	do{
		char cbuf[1024];
//		msgpack_sbuffer *buffer = msgpack_sbuffer_new();
//		msgpack_packer *pk = msgpack_packer_new(buffer, msgpack_sbuffer_write);

		ms_update();

//		msgpack_sbuffer_clear(buffer);
//		msgpack_pack_float(pk, ypr[YAW]);
//		msgpack_pack_float(pk, ypr[PITCH]);
//		msgpack_pack_float(pk, ypr[ROLL]);
//		msgpack_pack_float(pk, temp);
//		msgpack_packer_free(pk);

		snprintf(cbuf, 1024, "[%f, %f, %f, %f]", ypr[YAW], ypr[PITCH], ypr[ROLL], temp);

		rc = zmq_msg_init_data(&msg, cbuf, strlen(cbuf), NULL, NULL);
		zmq_send(pub, &msg, 0);

//		printf("yaw = %2.1f\tpitch = %2.1f\troll = %2.1f\ttemperature = %2.1f\tcompass = %2.1f, %2.1f, %2.1f\n",
//		 ypr[YAW], ypr[PITCH],
//		 ypr[ROLL],temp,compass[0],compass[1],compass[2]);
		delay_ms(5);
	}while(1);

	return 0;
}

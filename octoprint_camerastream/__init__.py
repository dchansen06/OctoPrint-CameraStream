import octoprint.plugin;
from octoprint.schema.webcam import Webcam, WebcamCompatibility;
import flask;
import cv2;
import multiprocessing;
import time;

class CameraStreamPlugin(octoprint.plugin.StartupPlugin,
			octoprint.plugin.BlueprintPlugin,
			octoprint.plugin.WebcamProviderPlugin):

	vid = cv2.VideoCapture(0);
	fps = 1;
	def _snapshot_as_bytes(self):
		self._logger.info("Snapshotting");
		if not self.vid.isOpened():
			return bytes("Cannot open", "utf-8");
		self.vid.read();
		ret, frame = self.vid.read();
		if not ret:
			return bytes("Cannot read", "utf-8");
		ret, buffer = cv2.imencode(".jpg", frame);
		if not ret:
			return bytes("Cannot convert", "utf-8");
		return buffer.tobytes();

	def _stream_as_bytes(self):
		while(True):
			self._logger.info("Stream shot");
			yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
			yield self._snapshot_as_bytes(self);
			yield b"\r\n";
			time.sleep(1.0 / fps);
	
	@octoprint.plugin.BlueprintPlugin.route("/stream", methods = ["GET"])
	def stream_handler(self):
		response = flask.Response(self._stream_as_bytes(), mimetype="multipart/x-mixed-replace; boundary=frame");
		return response

	@octoprint.plugin.BlueprintPlugin.route("/snapshot", methods = ["GET"])
	def snapshot_handler(self):
		self._logger.info(request.args);
		response = flask.make_response(self._snapshot_as_bytes());
		response.headers["Content-Type"] = "image/jpg";
		if "reload" in request.args:
			response.headers["Reload"] = 1 / self.fps;
		return response;

	def on_after_startup(self):
		self._logger.info("Configuring camera stream");

		self._logger.info("Did stuff");
		self.vid.set(cv2.CAP_PROP_BUFFERSIZE, 1);
		self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, 640);
		self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 480);

		if not self.vid.isOpened():
			self._logger.info("Never opened");

	def get_webcam_configurations(self):
		return [
			Webcam(
				name = "camerastream",
				displayName = "Camera Stream",
				canSnapshot = True,
				snapshot = "Internal Camera Stream",
				compat = WebcamCompatibility(
					snapshot = "/api/plugin/camerastream?snapshot",
					stream = "/api/plugin/camerastream?stream",
				)
			)
		]

	def take_webcam_snapshot(self):
		return self._snapshot_as_bytes();

	def get_update_information(self):
		return dict(
			camerastream = dict(
				displayName = f"{self._plugin_name} Plugin",
				displayVersion = self._plugin_version,
				type = "github_release",
				user = "dchansen06",
				repo = "OctoPrint-CameraStream",
				current = self._plugin_version,
				pip = "https://github.com/dchansen06/OctoPrint-CameraStream/archive/{target_version}.zip",
			)
		)

__plugin_name__ = "Camera Stream";
__plugin_pythoncompat__ = ">=3.7,<4";
__plugin_implementation__ = CameraStreamPlugin();
__plugin_hooks = {
	"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
}

#import cv2;
#vid = cv2.VideoCapture(0);
#vid.set(cv2.CAP_PROP_FRAME_WIDTH, 640);
#vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 480);
#
#while(True):
#	if not vid.isOpened():
#		break;
#
#	ret, frame = vid.read();
#
#	if not ret:
#		break;
#
#	cv2.imshow("Camera Frame", frame);
#	if cv2.waitKey(1) & 0xFF == ord('q'):
#		break;
#
#vid.release();
#cv2.destroyAllWindows();

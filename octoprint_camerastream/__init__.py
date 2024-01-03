import octoprint.plugin;
from octoprint.schema.webcam import Webcam, WebcamCompatibility;
import flask;
import cv2;
import multiprocessing;
import time;

class CameraStreamPlugin(octoprint.plugin.StartupPlugin,
			octoprint.plugin.SimpleApiPlugin,
			octoprint.plugin.WebcamProviderPlugin,
			octoprint.plugin.RestartNeedingPlugin,
			octoprint.plugin.SettingsPlugin,
			octoprint.plugin.TemplatePlugin):

	CameraID = 0;
	vid = cv2.VideoCapture(CameraID);
	fps = 1;

	def get_template_vars(self):
		return dict(
			self.cameraID = self._settings.get(["cameraID"]),
			self.fps = self._settings.get(["fps"]),
		)

	def get_template_configs(self):
		return [{
			"type": "webcam",
			"name": "Camera Stream",
			"template": "camerastream_webcam.jinja2",
		}]

	def get_settings_defaults(self):
		return dict(
			cameraID=0,
			fps=1,
		)

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

#	def get_api_commands(self):
#		return dict();

#	def on_api_command(self, command, data):
#		self._logger.info("Do nothing");

	def on_api_get(self, request):
		self._logger.info("Handling snapshot");
		response = flask.make_response(self._snapshot_as_bytes());
		response.headers["Content-Type"] = "image/jpg";
		response.headers["Pragma"] = "no-cache";
		response.headers["Cache-Control"] = "max-age=0, must-revalidate, no-store";
		
		if "stream" in request.args or "mjpg" in request.args:
			response.headers["Refresh"] = 1.0 / self.fps;
		if "fps" in request.args or "FPS" in request.args:
			response = flask.make_response(self.fps);
		
		return response;
	
	def on_after_startup(self):
		self._logger.info("Configuring camera stream");
		self.vid.set(cv2.CAP_PROP_BUFFERSIZE, 1);
		self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, 640);
		self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 480);

		if not self.vid.isOpened():
			self._logger.info("Never opened");

		self.CameraID = self._settings.get_int(["cameraID"])
		self.fps = self._settings.get_int(["fps"])

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
		return {
			"camerastream": {
				"displayName": "Camera Stream Plugin",
				"displayVersion": self._plugin_version,
				"type": "github_release",
				"user": "dchansen06",
				"repo": "OctoPrint-CameraStream",
				"current": self._plugin_version,
				"pip": "https://github.com/dchansen06/OctoPrint-CameraStream/archive/{target_version}.zip",
			}
		}

__plugin_name__ = "Camera Stream";
__plugin_pythoncompat__ = ">=3.7,<4";
__plugin_implementation__ = CameraStreamPlugin();
__plugin_hooks = {
	"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
}

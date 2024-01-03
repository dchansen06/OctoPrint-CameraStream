setInterval(document.getElementById("webcam_image").src = document.getElementById("webcam_image").src, 1.0 / OctoPrintClient.settings.getPluginSettings(camerastream, fps));

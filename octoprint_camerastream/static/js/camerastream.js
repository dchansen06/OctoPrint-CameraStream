setInterval(document.getElementById("webcam_image").src = document.getElementById("webcam_image").src, 1.0 / OctoPrint.settings.getPluginSettings("camerastream", "fps"));

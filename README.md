# ArvanCloud Video Upload Module

This module demonstrates how to upload videos to the [ArvanCloud VOD Platform](https://www.arvancloud.ir/products/video-platform) using Python and their public API.

##  Prerequisites

* An ArvanCloud account.
* A created video channel (can be created manually or via API).
* ArvanCloud API Key.
* Python 3.7+
* `requests` and `tuspy` libraries installed.

##  Installation

```bash
pip install requests 
pip install tuspy
```

##  Upload Flow

The general steps to upload a video are:

1. **Create a Channel**

   * You can create it manually from your Arvan dashboard, or using API.
   * In this module, we assume one default channel is used.

2. **Get Upload URL**

   * A `POST` request is sent to create a new file.
   * The response will contain an upload URL for temporary storage.

3. **Upload with tuspy**

   * The file is uploaded using the `tuspy` client with the `PATCH` method.
   * Once finished, an ID will be returned for the uploaded file.

4. **(Optional) Create Watermark / Subtitle**

   * You can create watermarks or subtitles manually or through the API.

5. **Convert File to Video**

   * A final `POST` request will move the temporary file to the videos section.
   * Watermark and subtitle settings can be included if needed.

##  Notes

* Always read Arvan's [official API documentation](https://napi.arvancloud.ir) before integrating. Endpoints or parameters may change.
* You can manage multiple channels if required.
* if you have any question contact with me: (daniyal.akhavan@gmail.com)



# arvan-python-video-upload

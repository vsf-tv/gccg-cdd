### Application Reference Design (ARD)

**Primary Functions**
* Communicates with a locally running TR-12 SDK.
* Communicates with the device's native control API.
* Translates between the device's native control API and the TR-12 models.

**How the ARD Works**
* Simulates a 1-channel encoder.
* Runs the TR-12 Client SDK.
* Handles communication between the underlying device API and the SDK.
    * A callback mechanism proxies `update_*` and `get_*` calls to the underlying encoder.

**Operational Details**
* Instantiates a `tr12_shim`.
* Displays real-time information to `stdout` (e.g., Pairing, Connection Status).
* **Startup:** Automatically establishes a connection.
* **Main Loop:** Continuously handles the following events:
    * Get Connection Status
    * Get Desired Configuration Update
    * Report Actual Configuration and Status

**Shim and Callback Mechanics**
The shim and callbacks provide the logic needed to translate between TR-12 models and native APIs.

* **The Shim:** * Contains Update and Get methods to map TR-12 models to the device's specific API.
    * Populates TR-12 Status and Actual Configuration models based on the native device's current state.
* **Applying Desired Configuration (via Client SDK):**
    * Traverses the Configuration model.
    * Triggers

**Setup and Run**:
- Path Setup: update FFMPEG_PATH in simple_encoder.py
- Start the client SDK process:  See README
- Start the ARD: python3 application.py --host_id <host_id>
  - Looks in src/host_configuration for <host_id>.json 

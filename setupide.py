from flask import Flask, Response, stream_with_context, render_template_string
import subprocess
import time
import threading
import os

app = Flask(__name__)

# ================= Commands to run =================

COMMANDS = [
    "echo '🚀 Starting Termux environment setup for AndroStudio...'",

    # 1️⃣ Directorie 
    "mkdir -p ~/AndroStudioProject",
    
    "pkg install -y python",
    "pkg install -y python3",
    "pkg install -y wget",
    "pkg install -y curl",
    "pkg install -y unzip",
    "pkg install -y openjdk-17",
    "pkg install -y gradle",
    "pkg install -y file",
    "pip install gdown",
    "pip install flask",
    "pip install flask-cors",
    "pip install werkzeug",
    "pip install ansi2html",

    # 3️⃣ Clone AndroStudio repo
    "git clone https://github.com/Jahangir-Alam-Hridoy/AndroStudio.git",

      # 4️⃣ Download android-sdk
      
      "gdown 'https://drive.google.com/uc?id=14PCNnbftUmbUXX0RCU6oTGv1JUVS49PR'",
      # unzip android-sdk
      "unzip android-sdk-aarch64.zip",


    # 6️⃣ Environment variables
    "echo '✅ Setting environment variables...'",
    "echo 'export ANDROID_HOME=$HOME/android-sdk' >> ~/.bashrc",
    "echo 'export ANDROID_SDK_ROOT=$ANDROID_HOME' >> ~/.bashrc",
    "echo 'export PATH=$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH' >> ~/.bashrc",
    "echo 'export JAVA_HOME=$(dirname $(dirname $(which java)))' >> ~/.bashrc",
    "echo 'for ver in $ANDROID_HOME/build-tools/*; do export PATH=$ver:$PATH; done' >> ~/.bashrc",
    "echo 'export PATH=$PATH:$JAVA_HOME/bin:$HOME' >> ~/.bashrc",
    "source ~/.bashrc",



    "echo '🎉 Android SDK setup complete! Everything is ready to run AndroStudio!'"
]

# ================= Background Process Output =================
def generate_output():
    try:
        total_commands = len(COMMANDS)
        for index, cmd in enumerate(COMMANDS):
            # Calculate progress percentage - more accurate calculation
            progress = int(((index) / total_commands) * 100)
            yield f"data: PROGRESS:{progress}\n\n"
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                shell=True,
                bufsize=1,  # Line buffered
                universal_newlines=True
            )
            
            for line in iter(process.stdout.readline, ''):
                if line:
                    yield f"data: {line.rstrip()}\n\n"
                    time.sleep(0.05)
            
            process.stdout.close()
            return_code = process.wait()
            
            if return_code == 0:
                yield f"data: ✅ Command completed successfully\n\n"
            else:
                yield f"data: ⚠️ Command finished with exit code {return_code}\n\n"

        # Final progress update
        yield f"data: PROGRESS:100\n\n"
        yield f"data: 🎉 All setup tasks completed!\n\n"
        
        # Give time for final messages to reach client
        time.sleep(1)
        
        # Auto shutdown server
        threading.Thread(target=lambda: (time.sleep(2), os._exit(0))).start()

    except Exception as e:
        yield f"data: ❌ Error: {str(e)}\n\n"
    finally:
        yield "data: [DONE]\n\n"

# ================= Flask Routes =================
@app.route('/')
def index():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Android IDE Setup</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { margin: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1f1f1f; color: #e0e0e0; }
            .header { background-color: #3c3f41; padding: 15px 30px; font-size: 1.5em; font-weight: bold; text-align: center; }
            .container { padding: 20px; max-width: 100%; }
            .progress-container { margin: 20px 0; width: 100%; background-color: #2c2f33; border-radius: 5px; overflow: hidden; height: 25px; }
            .progress-bar { width: 0%; height: 100%; background-color: #4caf50; transition: width 0.3s ease; }
            .progress-text { text-align: center; margin-top: 5px; font-size: 0.9em; color: #aaaaaa; }
            pre { background-color: #252526; padding: 15px; border-radius: 5px; height: 50vh; overflow-y: auto; white-space: pre-wrap; margin-top: 20px; font-family: 'Courier New', monospace; }
            .footer { text-align: center; padding: 10px; font-size: 0.9em; color: #aaaaaa; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="header">AndroStudio - Setup Wizard</div>
        <div class="container">
            <h2>Installing Required Tools</h2>
            <div class="progress-container">
                <div class="progress-bar" id="progressBar"></div>
            </div>
            <div class="progress-text" id="progressText">0% Complete</div>
            <pre id="terminal">Initializing setup process...\n</pre>
        </div>
        <div class="footer">Powered by AndroStudio</div>

        <script>
            const terminal = document.getElementById('terminal');
            const progressBar = document.getElementById('progressBar');
            const progressText = document.getElementById('progressText');
            let isComplete = false;
            
            const evtSource = new EventSource("/stream");
            
            evtSource.onmessage = function(e) {
                if(e.data === "[DONE]") {
                    isComplete = true;
                    evtSource.close();
                    terminal.innerHTML += "\\n✅ Setup process completed! You can now close this window.";
                    progressBar.style.width = "100%";
                    progressText.textContent = "100% Complete - Setup Finished!";
                    return;
                }
                
                if(e.data.startsWith("PROGRESS:")) {
                    const progress = e.data.split(":")[1];
                    progressBar.style.width = progress + "%";
                    progressText.textContent = progress + "% Complete";
                } else {
                    terminal.innerHTML += e.data + "\\n";
                    terminal.scrollTop = terminal.scrollHeight;
                }
            };
            
            evtSource.onerror = function(e) {
                if (!isComplete) {
                    terminal.innerHTML += "\\n⚠️ Connection to server lost. Setup may still be running...";
                }
            };
            
            // Prevent accidental navigation
            window.addEventListener('beforeunload', function(e) {
                if (!isComplete) {
                    e.preventDefault();
                    e.returnValue = '';
                }
            });
        </script>
    </body>
    </html>
    """
    return render_template_string(html_content)

@app.route('/stream')
def stream():
    return Response(stream_with_context(generate_output()), mimetype='text/event-stream')

# ================= Run Server =================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=38575, debug=False, threaded=True)






from flask import Flask, jsonify
from dotenv import load_dotenv
import subprocess
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

@app.route('/')
def home():
    return jsonify({
        'message': 'Hello World',
        'status': 'success'
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'message': 'Route not found',
        'status': 'error'
    }), 404

def get_gpu_info():
    try:
        # Run nvidia-smi command
        result = subprocess.run(['nvidia-smi', '--query-gpu=gpu_name,memory.used,memory.total,temperature.gpu,utilization.gpu', 
                               '--format=csv,noheader,nounits'], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            return {"error": "No NVIDIA GPU found"}

        # Parse output
        gpus = []
        for line in result.stdout.strip().split('\n'):
            name, mem_used, mem_total, temp, util = line.split(', ')
            gpus.append({
                "name": name,
                "memory_used": float(mem_used),
                "memory_total": float(mem_total),
                "temperature": float(temp),
                "utilization": float(util)
            })
        
        return {"gpus": gpus}
    except Exception as e:
        return {"error": str(e)}

# Add new endpoint for GPU info
@app.route('/gpu')
def gpu_status():
    return jsonify(get_gpu_info())

if __name__ == '__main__':
    app.run(
        host=os.getenv('HOST', 'localhost'),
        port=int(os.getenv('PORT', 5048)),
        debug=os.getenv('MODE') == 'dev'
    )
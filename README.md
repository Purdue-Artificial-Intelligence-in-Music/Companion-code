# Companion

Companion is your on-demand accompanist, allowing you to practice with professional-quality accompaniment anytime, anywhere.

## System Requirements
- **OS**: Windows 10/11 or Linux (macOS may work but is untested)
- **Memory**: 16 GB RAM (recommended)
- **Disk Space**: 10 GB for library installations
- **Audio**: Microphone and headphones (to prevent feedback)

## Getting Started

### Running the Backend Server Locally
1. Open a terminal and navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Run this command in a Python 3.8 conda environment to install all dependencies:
   ```bash
   python setup.py install
   ```
3. Start the Flask server:
   ```bash
   python app.py
   ```

### Running the Frontend Locally
1. Install Node.js from [nodejs.org](https://nodejs.org/en).
2. Install the Expo CLI:
   ```bash
   npm install -g expo-cli
   ```
3. Navigate to the frontend directory:
   ```bash
   cd frontend/companion-app
   ```
4. Install project dependencies:
   ```bash
   npm install
   ```
5. Start the frontend:
   ```bash
   npm run web
   ```

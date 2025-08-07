@echo off
echo ========================================
echo DÉMARRAGE LEO-IN BACKEND COMPLET
echo ========================================

cd /d "c:\Users\YOOSURF\Stage-Leoni\Backend"

echo 🔍 Vérification de l'environnement Python...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Python non trouvé!
    pause
    exit /b 1
)

echo 📦 Installation des dépendances...
pip install flask flask-cors pymongo python-dotenv bcrypt pyjwt requests

echo 🚀 Démarrage du serveur Flask avec les modules News & Chat...
echo.
echo 📰 Modules disponibles:
echo   - Authentication (Login/Register)
echo   - News (Actualités avec interactions)
echo   - Chat (Conversations en temps réel)
echo   - Profile Management
echo   - Document Requests
echo.
echo 🌐 Serveur disponible sur: http://localhost:5000
echo 📊 Base de données: MongoDB Atlas (LeoniApp)
echo.
echo ⏹️  Appuyez sur Ctrl+C pour arrêter
echo.

python app.py

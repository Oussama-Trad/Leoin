@echo off
echo ============================================
echo     LEONI APP - DEMARRAGE DEVELOPPEMENT
echo ============================================
echo.

echo [1/3] Demarrage du serveur backend Flask...
start "Backend Server" cmd /k "cd Backend && python app.py"

echo [2/3] Attente de 5 secondes pour que le serveur démarre...
timeout /t 5

echo [3/3] Demarrage de ngrok pour exposer le serveur...
start "Ngrok Tunnel" cmd /k "ngrok http 5000"

echo.
echo ============================================
echo     CONFIGURATION TERMINEE
echo ============================================
echo.
echo INSTRUCTIONS :
echo 1. Attendez que ngrok affiche une URL HTTPS
echo 2. Copiez cette URL (ex: https://abc123.ngrok.io)
echo 3. Ouvrez l'app mobile
echo 4. Cliquez sur l'icône paramètres (⚙️) sur l'écran de connexion
echo 5. Collez l'URL ngrok et cliquez "Mettre à jour l'URL"
echo 6. Testez la connexion
echo.
echo REMARQUE : L'URL ngrok change à chaque redémarrage !
echo Pour une URL fixe, créez un compte gratuit sur ngrok.com
echo.
pause

// Test simple pour vérifier la connexion
const testConnection = async () => {
  try {
    console.log('Testing connection to backend...');
    
    const response = await fetch('http://localhost:5000/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: 'y@gmail.com',
        password: 'yyyyyy'
      })
    });
    
    console.log('Response status:', response.status);
    console.log('Response headers:', response.headers);
    
    const data = await response.json();
    console.log('Response data:', data);
    
    if (data.success) {
      console.log('✅ Connexion réussie!');
      console.log('Token:', data.token);
      console.log('User:', data.user);
    } else {
      console.log('❌ Connexion échouée:', data.message);
    }
  } catch (error) {
    console.error('❌ Erreur de connexion:', error);
  }
};

// Exécuter le test
testConnection();

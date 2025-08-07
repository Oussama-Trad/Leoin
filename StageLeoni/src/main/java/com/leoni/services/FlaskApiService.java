package com.leoni.services;

import com.leoni.dto.UserDTO;
import com.leoni.models.Admin;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.UriComponentsBuilder;

import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.HashMap;

/**
 * Service pour intégrer l'API Flask du backend commun
 * Ce service permet au Spring Boot d'utiliser l'API de filtrage Flask
 */
@Service
public class FlaskApiService {

    @Value("${flask.api.base-url:http://localhost:5000}")
    private String flaskBaseUrl;

    private final RestTemplate restTemplate;

    public FlaskApiService() {
        this.restTemplate = new RestTemplate();
    }

    /**
     * Authentifier un admin via l'API Flask
     * @param username nom d'utilisateur
     * @param password mot de passe
     * @return token JWT si succès, null sinon
     */
    public String authenticateAdmin(String username, String password) {
        try {
            String url = flaskBaseUrl + "/api/admin/auth/login";
            
            Map<String, String> request = new HashMap<>();
            request.put("username", username);
            request.put("password", password);
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<Map<String, String>> entity = new HttpEntity<>(request, headers);
            
            ResponseEntity<Map> response = restTemplate.postForEntity(url, entity, Map.class);
            
            if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
                Map<String, Object> body = response.getBody();
                if (Boolean.TRUE.equals(body.get("success"))) {
                    return (String) body.get("token");
                }
            }
            
            return null;
        } catch (Exception e) {
            System.err.println("Erreur authentification Flask: " + e.getMessage());
            return null;
        }
    }

    /**
     * Récupérer les employés filtrés selon les permissions admin
     * @param adminToken token JWT de l'admin
     * @param department département à filtrer (optionnel)
     * @param location location à filtrer (optionnel)
     * @param role rôle de l'admin (ADMIN/SUPERADMIN)
     * @return liste des employés filtrés
     */
    public List<Map<String, Object>> getFilteredEmployees(String adminToken, String department, String location, String role) {
        try {
            UriComponentsBuilder builder = UriComponentsBuilder
                .fromHttpUrl(flaskBaseUrl + "/api/admin/employees/filtered-extended");
            
            if (department != null && !department.isEmpty()) {
                builder.queryParam("department", department);
            }
            if (location != null && !location.isEmpty()) {
                builder.queryParam("location", location);
            }
            if (role != null && !role.isEmpty()) {
                builder.queryParam("role", role);
            }
            
            HttpHeaders headers = new HttpHeaders();
            headers.set("Authorization", "Bearer " + adminToken);
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<?> entity = new HttpEntity<>(headers);
            
            ResponseEntity<Map> response = restTemplate.exchange(
                builder.toUriString(),
                HttpMethod.GET,
                entity,
                Map.class
            );
            
            if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
                Map<String, Object> body = response.getBody();
                if (Boolean.TRUE.equals(body.get("success"))) {
                    return (List<Map<String, Object>>) body.get("employees");
                }
            }
            
            return Arrays.asList();
        } catch (Exception e) {
            System.err.println("Erreur récupération employés Flask: " + e.getMessage());
            return Arrays.asList();
        }
    }

    /**
     * Créer une nouvelle actualité via l'API Flask
     * @param adminToken token JWT de l'admin
     * @param title titre de l'actualité
     * @param content contenu de l'actualité
     * @param targetDepartments départements ciblés
     * @param targetLocations locations ciblées
     * @return true si succès, false sinon
     */
    public boolean createNews(String adminToken, String title, String content, 
                             List<String> targetDepartments, List<String> targetLocations) {
        try {
            String url = flaskBaseUrl + "/api/admin/news/create-extended";
            
            Map<String, Object> request = new HashMap<>();
            request.put("title", title);
            request.put("content", content);
            request.put("targetDepartments", targetDepartments);
            request.put("targetLocations", targetLocations);
            request.put("priority", "normal");
            
            HttpHeaders headers = new HttpHeaders();
            headers.set("Authorization", "Bearer " + adminToken);
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(request, headers);
            
            ResponseEntity<Map> response = restTemplate.postForEntity(url, entity, Map.class);
            
            if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
                Map<String, Object> body = response.getBody();
                return Boolean.TRUE.equals(body.get("success"));
            }
            
            return false;
        } catch (Exception e) {
            System.err.println("Erreur création news Flask: " + e.getMessage());
            return false;
        }
    }

    /**
     * Récupérer les demandes de documents filtrées
     * @param adminToken token JWT de l'admin
     * @param department département à filtrer
     * @param location location à filtrer
     * @param role rôle de l'admin
     * @return liste des demandes de documents
     */
    public List<Map<String, Object>> getFilteredDocumentRequests(String adminToken, String department, String location, String role) {
        try {
            UriComponentsBuilder builder = UriComponentsBuilder
                .fromHttpUrl(flaskBaseUrl + "/api/admin/documents/filtered-extended");
            
            if (department != null && !department.isEmpty()) {
                builder.queryParam("department", department);
            }
            if (location != null && !location.isEmpty()) {
                builder.queryParam("location", location);
            }
            if (role != null && !role.isEmpty()) {
                builder.queryParam("role", role);
            }
            
            HttpHeaders headers = new HttpHeaders();
            headers.set("Authorization", "Bearer " + adminToken);
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<?> entity = new HttpEntity<>(headers);
            
            ResponseEntity<Map> response = restTemplate.exchange(
                builder.toUriString(),
                HttpMethod.GET,
                entity,
                Map.class
            );
            
            if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
                Map<String, Object> body = response.getBody();
                if (Boolean.TRUE.equals(body.get("success"))) {
                    return (List<Map<String, Object>>) body.get("documents");
                }
            }
            
            return Arrays.asList();
        } catch (Exception e) {
            System.err.println("Erreur récupération documents Flask: " + e.getMessage());
            return Arrays.asList();
        }
    }

    /**
     * Mettre à jour le statut d'une demande de document
     * @param adminToken token JWT de l'admin
     * @param documentId ID du document
     * @param newStatus nouveau statut
     * @return true si succès, false sinon
     */
    public boolean updateDocumentStatus(String adminToken, String documentId, String newStatus) {
        try {
            String url = flaskBaseUrl + "/api/admin/documents/" + documentId + "/status-extended";
            
            Map<String, String> request = new HashMap<>();
            request.put("newStatus", newStatus);
            
            HttpHeaders headers = new HttpHeaders();
            headers.set("Authorization", "Bearer " + adminToken);
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<Map<String, String>> entity = new HttpEntity<>(request, headers);
            
            ResponseEntity<Map> response = restTemplate.exchange(
                url,
                HttpMethod.PUT,
                entity,
                Map.class
            );
            
            if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
                Map<String, Object> body = response.getBody();
                return Boolean.TRUE.equals(body.get("success"));
            }
            
            return false;
        } catch (Exception e) {
            System.err.println("Erreur mise à jour statut document Flask: " + e.getMessage());
            return false;
        }
    }

    /**
     * Récupérer les départements et locations disponibles
     * @return map avec les départements et locations
     */
    public Map<String, Object> getDepartmentsAndLocations() {
        try {
            String url = flaskBaseUrl + "/api/admin/departments-locations";
            
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            
            HttpEntity<?> entity = new HttpEntity<>(headers);
            
            ResponseEntity<Map> response = restTemplate.exchange(
                url,
                HttpMethod.GET,
                entity,
                Map.class
            );
            
            if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
                return response.getBody();
            }
            
            return new HashMap<>();
        } catch (Exception e) {
            System.err.println("Erreur récupération départements/locations Flask: " + e.getMessage());
            return new HashMap<>();
        }
    }
}

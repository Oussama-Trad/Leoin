package com.leoni.controllers;

import com.leoni.dto.DocumentRequestDTO;
import com.leoni.dto.UpdateStatusRequest;
import com.leoni.exceptions.DocumentRequestNotFoundException;
import com.leoni.exceptions.InvalidStatusException;
import com.leoni.exceptions.UserNotFoundException;
import com.leoni.services.DocumentRequestService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/documents")
@CrossOrigin(origins = "*")
public class DocumentController {
    
    @Autowired
    private DocumentRequestService documentRequestService;
    
    /**
     * Get all document requests
     * @return List of all document requests
     */
    @GetMapping
    public ResponseEntity<List<DocumentRequestDTO>> getAllDocumentRequests() {
        try {
            List<DocumentRequestDTO> documents = documentRequestService.getAllDocumentRequests();
            return ResponseEntity.ok(documents);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    /**
     * Get document request by ID
     * @param id the document request ID
     * @return DocumentRequestDTO
     */
    @GetMapping("/{id}")
    public ResponseEntity<DocumentRequestDTO> getDocumentRequestById(@PathVariable String id) {
        try {
            DocumentRequestDTO document = documentRequestService.getDocumentRequestById(id);
            return ResponseEntity.ok(document);
        } catch (DocumentRequestNotFoundException e) {
            return ResponseEntity.notFound().build();
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    /**
     * Get document requests by user ID
     * @param userId the user ID
     * @return List of document requests for the user
     */
    @GetMapping("/user/{userId}")
    public ResponseEntity<List<DocumentRequestDTO>> getDocumentRequestsByUserId(@PathVariable String userId) {
        try {
            List<DocumentRequestDTO> documents = documentRequestService.getDocumentRequestsByUserId(userId);
            return ResponseEntity.ok(documents);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    /**
     * Get document requests by status
     * @param status the status to filter by
     * @return List of document requests with the specified status
     */
    @GetMapping("/status/{status}")
    public ResponseEntity<List<DocumentRequestDTO>> getDocumentRequestsByStatus(@PathVariable String status) {
        try {
            List<DocumentRequestDTO> documents = documentRequestService.getDocumentRequestsByStatus(status);
            return ResponseEntity.ok(documents);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    /**
     * Get document requests by type
     * @param type the document type
     * @return List of document requests of the specified type
     */
    @GetMapping("/type/{type}")
    public ResponseEntity<List<DocumentRequestDTO>> getDocumentRequestsByType(@PathVariable String type) {
        try {
            List<DocumentRequestDTO> documents = documentRequestService.getDocumentRequestsByType(type);
            return ResponseEntity.ok(documents);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    /**
     * Create a new document request
     * @param documentRequestDTO the document request data
     * @return created DocumentRequestDTO
     */
    @PostMapping
    public ResponseEntity<Map<String, Object>> createDocumentRequest(@RequestBody DocumentRequestDTO documentRequestDTO) {
        Map<String, Object> response = new HashMap<>();
        
        try {
            DocumentRequestDTO createdDocument = documentRequestService.createDocumentRequest(documentRequestDTO);
            response.put("success", true);
            response.put("message", "Demande de document créée avec succès");
            response.put("document", createdDocument);
            return ResponseEntity.status(HttpStatus.CREATED).body(response);
        } catch (UserNotFoundException e) {
            response.put("success", false);
            response.put("message", e.getMessage());
            response.put("errorCode", e.getErrorCode());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
        } catch (Exception e) {
            response.put("success", false);
            response.put("message", "Erreur lors de la création de la demande: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
        }
    }
    
    /**
     * Update document request status
     * @param updateStatusRequest the status update request
     * @return updated DocumentRequestDTO
     */
    @PutMapping("/status")
    public ResponseEntity<Map<String, Object>> updateDocumentStatus(@RequestBody UpdateStatusRequest updateStatusRequest) {
        Map<String, Object> response = new HashMap<>();
        
        try {
            // Validate request
            if (!updateStatusRequest.isValidStatus()) {
                response.put("success", false);
                response.put("message", "Statut invalide: " + updateStatusRequest.getNewStatus());
                response.put("errorCode", "INVALID_STATUS");
                return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
            }
            
            DocumentRequestDTO updatedDocument = documentRequestService.updateDocumentStatus(updateStatusRequest);
            response.put("success", true);
            response.put("message", "Statut mis à jour avec succès");
            response.put("document", updatedDocument);
            return ResponseEntity.ok(response);
        } catch (DocumentRequestNotFoundException e) {
            response.put("success", false);
            response.put("message", e.getMessage());
            response.put("errorCode", e.getErrorCode());
            return ResponseEntity.notFound().build();
        } catch (InvalidStatusException e) {
            response.put("success", false);
            response.put("message", e.getMessage());
            response.put("errorCode", e.getErrorCode());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(response);
        } catch (Exception e) {
            response.put("success", false);
            response.put("message", "Erreur lors de la mise à jour du statut: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
        }
    }
    
    /**
     * Delete a document request
     * @param id the document request ID
     * @return deletion result
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, Object>> deleteDocumentRequest(@PathVariable String id) {
        Map<String, Object> response = new HashMap<>();
        
        try {
            documentRequestService.deleteDocumentRequest(id);
            response.put("success", true);
            response.put("message", "Demande de document supprimée avec succès");
            return ResponseEntity.ok(response);
        } catch (DocumentRequestNotFoundException e) {
            response.put("success", false);
            response.put("message", e.getMessage());
            response.put("errorCode", e.getErrorCode());
            return ResponseEntity.notFound().build();
        } catch (Exception e) {
            response.put("success", false);
            response.put("message", "Erreur lors de la suppression de la demande: " + e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(response);
        }
    }
    
    /**
     * Search document requests by description
     * @param searchTerm the search term
     * @return List of matching document requests
     */
    @GetMapping("/search")
    public ResponseEntity<List<DocumentRequestDTO>> searchDocumentRequests(@RequestParam String searchTerm) {
        try {
            List<DocumentRequestDTO> documents = documentRequestService.searchDocumentRequestsByDescription(searchTerm);
            return ResponseEntity.ok(documents);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    /**
     * Get document requests statistics
     * @return Statistics about document requests
     */
    @GetMapping("/stats")
    public ResponseEntity<Map<String, Object>> getDocumentRequestsStats() {
        try {
            Map<String, Object> stats = new HashMap<>();
            
            // Count by status
            stats.put("enAttente", documentRequestService.getDocumentRequestsCountByStatus("en attente"));
            stats.put("enCours", documentRequestService.getDocumentRequestsCountByStatus("en cours"));
            stats.put("accepte", documentRequestService.getDocumentRequestsCountByStatus("accepté"));
            stats.put("refuse", documentRequestService.getDocumentRequestsCountByStatus("refusé"));
            
            // Total count
            long total = (Long) stats.get("enAttente") + (Long) stats.get("enCours") + 
                        (Long) stats.get("accepte") + (Long) stats.get("refuse");
            stats.put("total", total);
            
            return ResponseEntity.ok(stats);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    /**
     * Get available document statuses
     * @return List of available statuses
     */
    @GetMapping("/statuses")
    public ResponseEntity<Map<String, Object>> getAvailableStatuses() {
        Map<String, Object> response = new HashMap<>();
        response.put("statuses", List.of("en attente", "en cours", "accepté", "refusé"));
        response.put("descriptions", Map.of(
            "en attente", "Demande en attente de traitement",
            "en cours", "Demande en cours de traitement",
            "accepté", "Demande acceptée",
            "refusé", "Demande refusée"
        ));
        return ResponseEntity.ok(response);
    }
    
    /**
     * Health check endpoint
     * @return service status
     */
    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> healthCheck() {
        Map<String, Object> response = new HashMap<>();
        response.put("success", true);
        response.put("message", "Service documents opérationnel");
        response.put("timestamp", System.currentTimeMillis());
        return ResponseEntity.ok(response);
    }
}
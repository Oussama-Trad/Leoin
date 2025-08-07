package com.leoni.controllers;

import com.leoni.models.DocumentRequest;
import com.leoni.repositories.DocumentRequestRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.HashMap;
import java.util.Optional;

@RestController
@RequestMapping("/api/admin/documents")
@CrossOrigin(origins = "*")
public class AdminDocumentController {

    @Autowired
    private DocumentRequestRepository documentRequestRepository;

    /**
     * Get all documents for admin panel
     */
    @GetMapping
    public ResponseEntity<List<DocumentRequest>> getAllDocuments() {
        try {
            List<DocumentRequest> documents = documentRequestRepository.findAll();
            return ResponseEntity.ok(documents);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(null);
        }
    }

    /**
     * Get document by ID
     */
    @GetMapping("/{id}")
    public ResponseEntity<DocumentRequest> getDocumentById(@PathVariable String id) {
        try {
            Optional<DocumentRequest> document = documentRequestRepository.findById(id);
            return document.map(ResponseEntity::ok).orElse(ResponseEntity.notFound().build());
        } catch (Exception e) {
            return ResponseEntity.status(500).body(null);
        }
    }

    /**
     * Get documents by status
     */
    @GetMapping("/status/{status}")
    public ResponseEntity<List<DocumentRequest>> getDocumentsByStatus(@PathVariable String status) {
        try {
            List<DocumentRequest> documents = documentRequestRepository.findByCurrentStatus(status);
            return ResponseEntity.ok(documents);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(null);
        }
    }

    /**
     * Update document status
     */
    @PutMapping("/{id}/status")
    public ResponseEntity<Map<String, Object>> updateDocumentStatus(
            @PathVariable String id,
            @RequestBody Map<String, String> statusUpdate) {
        try {
            Optional<DocumentRequest> optionalDocument = documentRequestRepository.findById(id);
            if (!optionalDocument.isPresent()) {
                return ResponseEntity.notFound().build();
            }
            
            DocumentRequest document = optionalDocument.get();
            String newStatus = statusUpdate.get("status");
            
            if (newStatus != null) {
                document.getStatus().setCurrent(newStatus);
                document.setUpdatedAt(new java.util.Date());
                
                // Update progress steps
                document.getStatus().getProgress().forEach(step -> {
                    if (step.getStep().equals(newStatus)) {
                        step.setCompleted(true);
                        step.setDate(new java.util.Date());
                    }
                });
                
                documentRequestRepository.save(document);
            }
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "Document status updated successfully");
            response.put("document", document);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(createErrorResponse("Error updating document status: " + e.getMessage()));
        }
    }

    /**
     * Create new document request
     */
    @PostMapping
    public ResponseEntity<Map<String, Object>> createDocument(@RequestBody DocumentRequest documentRequest) {
        try {
            documentRequest.setCreatedAt(new java.util.Date());
            documentRequest.setUpdatedAt(new java.util.Date());
            
            // Initialize status if not provided
            if (documentRequest.getStatus() == null) {
                documentRequest.setStatus(new DocumentRequest.Status());
            }
            
            DocumentRequest savedDocument = documentRequestRepository.save(documentRequest);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "Document created successfully");
            response.put("document", savedDocument);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(createErrorResponse("Error creating document: " + e.getMessage()));
        }
    }

    /**
     * Update document
     */
    @PutMapping("/{id}")
    public ResponseEntity<Map<String, Object>> updateDocument(
            @PathVariable String id,
            @RequestBody DocumentRequest documentRequest) {
        try {
            Optional<DocumentRequest> optionalDocument = documentRequestRepository.findById(id);
            if (!optionalDocument.isPresent()) {
                return ResponseEntity.notFound().build();
            }
            
            DocumentRequest existingDocument = optionalDocument.get();
            existingDocument.setDocumentTypes(documentRequest.getDocumentTypes());
            existingDocument.setDescription(documentRequest.getDescription());
            existingDocument.setUpdatedAt(new java.util.Date());
            
            DocumentRequest updatedDocument = documentRequestRepository.save(existingDocument);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "Document updated successfully");
            response.put("document", updatedDocument);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(createErrorResponse("Error updating document: " + e.getMessage()));
        }
    }

    /**
     * Delete document
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, Object>> deleteDocument(@PathVariable String id) {
        try {
            Optional<DocumentRequest> document = documentRequestRepository.findById(id);
            if (!document.isPresent()) {
                return ResponseEntity.notFound().build();
            }
            
            documentRequestRepository.deleteById(id);
            
            Map<String, Object> response = new HashMap<>();
            response.put("success", true);
            response.put("message", "Document deleted successfully");
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(createErrorResponse("Error deleting document: " + e.getMessage()));
        }
    }

    /**
     * Get documents statistics
     */
    @GetMapping("/stats")
    public ResponseEntity<Map<String, Object>> getDocumentStats() {
        try {
            List<DocumentRequest> allDocuments = documentRequestRepository.findAll();
            
            Map<String, Object> stats = new HashMap<>();
            stats.put("total", allDocuments.size());
            
            // Count by status
            long pending = allDocuments.stream()
                .filter(doc -> "en attente".equals(doc.getStatus().getCurrent()))
                .count();
            long inProgress = allDocuments.stream()
                .filter(doc -> "en cours".equals(doc.getStatus().getCurrent()))
                .count();
            long accepted = allDocuments.stream()
                .filter(doc -> "accepté".equals(doc.getStatus().getCurrent()))
                .count();
            long rejected = allDocuments.stream()
                .filter(doc -> "refusé".equals(doc.getStatus().getCurrent()))
                .count();
            
            stats.put("pending", pending);
            stats.put("inProgress", inProgress);
            stats.put("accepted", accepted);
            stats.put("rejected", rejected);
            
            return ResponseEntity.ok(stats);
        } catch (Exception e) {
            return ResponseEntity.status(500).body(createErrorResponse("Error fetching document stats: " + e.getMessage()));
        }
    }

    // Helper methods
    private Map<String, Object> createErrorResponse(String message) {
        Map<String, Object> response = new HashMap<>();
        response.put("success", false);
        response.put("message", message);
        return response;
    }
}

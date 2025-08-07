package com.leoni.controllers;

import com.leoni.models.DocumentType;
import com.leoni.repositories.DocumentTypeRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Date;
import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api/admin/document-types")
@CrossOrigin(origins = "*")
public class DocumentTypeController {

    @Autowired
    private DocumentTypeRepository documentTypeRepository;

    // Get all document types
    @GetMapping
    public ResponseEntity<List<DocumentType>> getAllDocumentTypes() {
        List<DocumentType> documentTypes = documentTypeRepository.findAll();
        return ResponseEntity.ok(documentTypes);
    }

    // Get only active document types
    @GetMapping("/active")
    public ResponseEntity<List<DocumentType>> getActiveDocumentTypes() {
        List<DocumentType> activeDocumentTypes = documentTypeRepository.findByActiveTrue();
        return ResponseEntity.ok(activeDocumentTypes);
    }

    // Get document type by ID
    @GetMapping("/{id}")
    public ResponseEntity<DocumentType> getDocumentTypeById(@PathVariable String id) {
        Optional<DocumentType> documentType = documentTypeRepository.findById(id);
        return documentType.map(ResponseEntity::ok)
                          .orElse(ResponseEntity.notFound().build());
    }

    // Create new document type
    @PostMapping
    public ResponseEntity<?> createDocumentType(@RequestBody DocumentType documentType) {
        try {
            // Check if document type with same name already exists
            if (documentTypeRepository.existsByNameIgnoreCase(documentType.getName())) {
                return ResponseEntity.badRequest()
                    .body("Document type with name '" + documentType.getName() + "' already exists");
            }

            documentType.setCreatedAt(new Date());
            documentType.setUpdatedAt(new Date());
            DocumentType savedDocumentType = documentTypeRepository.save(documentType);
            return ResponseEntity.ok(savedDocumentType);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body("Error creating document type: " + e.getMessage());
        }
    }

    // Update document type
    @PutMapping("/{id}")
    public ResponseEntity<?> updateDocumentType(@PathVariable String id, @RequestBody DocumentType documentType) {
        try {
            Optional<DocumentType> existingDocumentType = documentTypeRepository.findById(id);
            if (existingDocumentType.isEmpty()) {
                return ResponseEntity.notFound().build();
            }

            // Check if another document type with same name exists (excluding current)
            DocumentType existing = documentTypeRepository.findByNameIgnoreCase(documentType.getName());
            if (existing != null && !existing.getId().equals(id)) {
                return ResponseEntity.badRequest()
                    .body("Document type with name '" + documentType.getName() + "' already exists");
            }

            DocumentType docTypeToUpdate = existingDocumentType.get();
            docTypeToUpdate.setName(documentType.getName());
            docTypeToUpdate.setDescription(documentType.getDescription());
            docTypeToUpdate.setActive(documentType.isActive());
            docTypeToUpdate.setUpdatedAt(new Date());

            DocumentType updatedDocumentType = documentTypeRepository.save(docTypeToUpdate);
            return ResponseEntity.ok(updatedDocumentType);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body("Error updating document type: " + e.getMessage());
        }
    }

    // Delete document type
    @DeleteMapping("/{id}")
    public ResponseEntity<?> deleteDocumentType(@PathVariable String id) {
        try {
            if (!documentTypeRepository.existsById(id)) {
                return ResponseEntity.notFound().build();
            }

            documentTypeRepository.deleteById(id);
            return ResponseEntity.ok().build();
        } catch (Exception e) {
            return ResponseEntity.badRequest().body("Error deleting document type: " + e.getMessage());
        }
    }

    // Toggle active status
    @PutMapping("/{id}/toggle-status")
    public ResponseEntity<?> toggleDocumentTypeStatus(@PathVariable String id) {
        try {
            Optional<DocumentType> documentType = documentTypeRepository.findById(id);
            if (documentType.isEmpty()) {
                return ResponseEntity.notFound().build();
            }

            DocumentType docType = documentType.get();
            docType.setActive(!docType.isActive());
            docType.setUpdatedAt(new Date());

            DocumentType updatedDocumentType = documentTypeRepository.save(docType);
            return ResponseEntity.ok(updatedDocumentType);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body("Error toggling document type status: " + e.getMessage());
        }
    }
}

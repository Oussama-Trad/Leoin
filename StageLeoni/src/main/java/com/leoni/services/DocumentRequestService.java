package com.leoni.services;

import com.leoni.dto.DocumentRequestDTO;
import com.leoni.dto.UpdateStatusRequest;
import com.leoni.exceptions.DocumentRequestNotFoundException;
import com.leoni.exceptions.InvalidStatusException;
import com.leoni.exceptions.UserNotFoundException;
import com.leoni.models.DocumentRequest;
import com.leoni.models.User;
import com.leoni.repositories.DocumentRequestRepository;
import com.leoni.repositories.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Date;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class DocumentRequestService {
    
    @Autowired
    private DocumentRequestRepository documentRequestRepository;
    
    @Autowired
    private UserRepository userRepository;
    
    /**
     * Get all document requests
     * @return List of DocumentRequestDTO
     */
    public List<DocumentRequestDTO> getAllDocumentRequests() {
        return documentRequestRepository.findAllByOrderByCreatedAtDesc()
                .stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }
    
    /**
     * Get document request by ID
     * @param id the document request ID
     * @return DocumentRequestDTO
     * @throws DocumentRequestNotFoundException if document request not found
     */
    public DocumentRequestDTO getDocumentRequestById(String id) {
        DocumentRequest documentRequest = documentRequestRepository.findById(id)
                .orElseThrow(() -> new DocumentRequestNotFoundException(id));
        return convertToDTO(documentRequest);
    }
    
    /**
     * Get document requests by user ID
     * @param userId the user ID
     * @return List of DocumentRequestDTO
     */
    public List<DocumentRequestDTO> getDocumentRequestsByUserId(String userId) {
        return documentRequestRepository.findByUserIdOrderByCreatedAtDesc(userId)
                .stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }
    
    /**
     * Get document requests by status
     * @param status the status to filter by
     * @return List of DocumentRequestDTO
     */
    public List<DocumentRequestDTO> getDocumentRequestsByStatus(String status) {
        return documentRequestRepository.findByCurrentStatus(status)
                .stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }
    
    /**
     * Create a new document request
     * @param documentRequestDTO the document request data
     * @return created DocumentRequestDTO
     * @throws UserNotFoundException if user not found
     */
    public DocumentRequestDTO createDocumentRequest(DocumentRequestDTO documentRequestDTO) {
        // Verify user exists
        User user = userRepository.findById(documentRequestDTO.getUserId())
                .orElseThrow(() -> new UserNotFoundException(documentRequestDTO.getUserId()));
        
        DocumentRequest documentRequest = convertToEntity(documentRequestDTO);
        documentRequest.setCreatedAt(new Date());
        documentRequest.setUpdatedAt(new Date());
        
        // Initialize status if not provided
        if (documentRequest.getStatus() == null) {
            DocumentRequest.Status status = new DocumentRequest.Status();
            documentRequest.setStatus(status);
        }
        
        DocumentRequest savedDocumentRequest = documentRequestRepository.save(documentRequest);
        
        // Add document reference to user
        user.addDocumentRequest(savedDocumentRequest.getId());
        userRepository.save(user);
        
        return convertToDTO(savedDocumentRequest);
    }
    
    /**
     * Update document request status
     * @param updateStatusRequest the status update request
     * @return updated DocumentRequestDTO
     * @throws DocumentRequestNotFoundException if document request not found
     * @throws InvalidStatusException if status transition is invalid
     */
    public DocumentRequestDTO updateDocumentStatus(UpdateStatusRequest updateStatusRequest) {
        DocumentRequest documentRequest = documentRequestRepository.findById(updateStatusRequest.getDocumentId())
                .orElseThrow(() -> new DocumentRequestNotFoundException(updateStatusRequest.getDocumentId()));
        
        String currentStatus = documentRequest.getStatus().getCurrent();
        String newStatus = updateStatusRequest.getNewStatus();
        
        // Validate status transition
        if (!isValidStatusTransition(currentStatus, newStatus)) {
            throw InvalidStatusException.invalidTransition(currentStatus, newStatus);
        }
        
        // Update status
        documentRequest.getStatus().setCurrent(newStatus);
        
        // Update progress steps
        updateProgressSteps(documentRequest, newStatus);
        
        documentRequest.setUpdatedAt(new Date());
        
        DocumentRequest savedDocumentRequest = documentRequestRepository.save(documentRequest);
        return convertToDTO(savedDocumentRequest);
    }
    
    /**
     * Delete a document request
     * @param id the document request ID
     * @throws DocumentRequestNotFoundException if document request not found
     */
    public void deleteDocumentRequest(String id) {
        DocumentRequest documentRequest = documentRequestRepository.findById(id)
                .orElseThrow(() -> new DocumentRequestNotFoundException(id));
        
        // Remove reference from user
        User user = userRepository.findById(documentRequest.getUserId()).orElse(null);
        if (user != null && user.getDocumentRequestIds() != null) {
            user.getDocumentRequestIds().remove(id);
            userRepository.save(user);
        }
        
        documentRequestRepository.deleteById(id);
    }
    
    /**
     * Get document requests count by status
     * @param status the status
     * @return count of documents with the status
     */
    public long getDocumentRequestsCountByStatus(String status) {
        return documentRequestRepository.countByCurrentStatus(status);
    }
    
    /**
     * Search document requests by description
     * @param searchTerm the search term
     * @return List of matching DocumentRequestDTO
     */
    public List<DocumentRequestDTO> searchDocumentRequestsByDescription(String searchTerm) {
        return documentRequestRepository.searchByDescription(searchTerm)
                .stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }
    
    /**
     * Get document requests by type
     * @param documentType the document type
     * @return List of DocumentRequestDTO
     */
    public List<DocumentRequestDTO> getDocumentRequestsByType(String documentType) {
        return documentRequestRepository.findByDocumentTypesContaining(documentType)
                .stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }
    
    /**
     * Validate status transition
     * @param currentStatus the current status
     * @param newStatus the new status
     * @return true if transition is valid
     */
    private boolean isValidStatusTransition(String currentStatus, String newStatus) {
        // Define valid transitions
        switch (currentStatus) {
            case "en attente":
                return "en cours".equals(newStatus) || "refusé".equals(newStatus);
            case "en cours":
                return "accepté".equals(newStatus) || "refusé".equals(newStatus);
            case "accepté":
            case "refusé":
                return false; // Final states
            default:
                return false;
        }
    }
    
    /**
     * Update progress steps based on new status
     * @param documentRequest the document request
     * @param newStatus the new status
     */
    private void updateProgressSteps(DocumentRequest documentRequest, String newStatus) {
        List<DocumentRequest.ProgressStep> progressSteps = documentRequest.getStatus().getProgress();
        
        for (DocumentRequest.ProgressStep step : progressSteps) {
            if (step.getStep().equals(newStatus)) {
                step.setCompleted(true);
                step.setDate(new Date());
                break;
            }
        }
    }
    
    /**
     * Convert DocumentRequest entity to DocumentRequestDTO
     * @param documentRequest the DocumentRequest entity
     * @return DocumentRequestDTO
     */
    private DocumentRequestDTO convertToDTO(DocumentRequest documentRequest) {
        DocumentRequestDTO dto = new DocumentRequestDTO();
        dto.setId(documentRequest.getId());
        dto.setUserId(documentRequest.getUserId());
        dto.setDocumentTypes(documentRequest.getDocumentTypes());
        dto.setDescription(documentRequest.getDescription());
        dto.setCreatedAt(documentRequest.getCreatedAt());
        dto.setUpdatedAt(documentRequest.getUpdatedAt());
        
        // Convert status
        if (documentRequest.getStatus() != null) {
            DocumentRequestDTO.StatusDTO statusDTO = new DocumentRequestDTO.StatusDTO();
            statusDTO.setCurrent(documentRequest.getStatus().getCurrent());
            
            // Convert progress steps
            List<DocumentRequestDTO.ProgressStepDTO> progressStepsDTO = documentRequest.getStatus().getProgress()
                    .stream()
                    .map(step -> new DocumentRequestDTO.ProgressStepDTO(step.getStep(), step.getDate(), step.isCompleted()))
                    .collect(Collectors.toList());
            statusDTO.setProgress(progressStepsDTO);
            
            dto.setStatus(statusDTO);
        }
        
        // Add user information for display
        User user = userRepository.findById(documentRequest.getUserId()).orElse(null);
        if (user != null) {
            dto.setUserFullName(user.getFirstName() + " " + user.getLastName());
            dto.setUserEmail(user.getAdresse1() != null ? user.getAdresse1() : ""); // Use primary email
            dto.setUserEmployeeId(user.getEmployeeId());
        }
        
        return dto;
    }
    
    /**
     * Convert DocumentRequestDTO to DocumentRequest entity
     * @param documentRequestDTO the DocumentRequestDTO
     * @return DocumentRequest entity
     */
    private DocumentRequest convertToEntity(DocumentRequestDTO documentRequestDTO) {
        DocumentRequest documentRequest = new DocumentRequest();
        documentRequest.setUserId(documentRequestDTO.getUserId());
        documentRequest.setDocumentTypes(documentRequestDTO.getDocumentTypes());
        documentRequest.setDescription(documentRequestDTO.getDescription());
        return documentRequest;
    }
}
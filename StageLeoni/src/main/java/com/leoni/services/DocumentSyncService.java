package com.leoni.services;

import com.leoni.models.DocumentRequest;
import com.leoni.models.User;
import com.leoni.repositories.DocumentRequestRepository;
import com.leoni.repositories.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.data.mongodb.core.query.Criteria;
import org.springframework.data.mongodb.core.query.Query;
import org.springframework.stereotype.Service;

import java.util.*;

/**
 * Service unifié pour la synchronisation des documents avec l'application mobile
 */
@Service
public class DocumentSyncService {
    
    @Autowired
    private DocumentRequestRepository documentRequestRepository;
    
    @Autowired
    private UserRepository userRepository;
    
    @Autowired
    private MongoTemplate mongoTemplate;
    
    /**
     * Récupérer les demandes de documents filtrées pour un admin
     */
    public Page<DocumentRequest> getFilteredDocumentRequestsForAdmin(String adminDepartment, String adminLocation, 
                                                                    String adminRole, int page, int size, String status) {
        
        System.out.println("DocumentSyncService: Filtrage demandes pour admin");
        System.out.println("Département: " + adminDepartment + ", Location: " + adminLocation + ", Rôle: " + adminRole);
        
        Criteria criteria = new Criteria();
        List<Criteria> conditions = new ArrayList<>();
        
        // Filtrage selon le rôle
        if (!"SUPERADMIN".equals(adminRole)) {
            // Admin normal : seulement les demandes des employés de son département/location
            if (adminDepartment != null && !adminDepartment.trim().isEmpty()) {
                conditions.add(Criteria.where("userDepartment").is(adminDepartment));
            }
            if (adminLocation != null && !adminLocation.trim().isEmpty()) {
                conditions.add(Criteria.where("userLocation").is(adminLocation));
            }
        }
        // SuperAdmin voit toutes les demandes
        
        // Filtre par statut si fourni
        if (status != null && !status.trim().isEmpty() && !"all".equals(status)) {
            conditions.add(Criteria.where("status.current").is(status));
        }
        
        // Appliquer les conditions
        if (!conditions.isEmpty()) {
            criteria = criteria.andOperator(conditions.toArray(new Criteria[0]));
        }
        
        // Créer la requête avec pagination
        Pageable pageable = PageRequest.of(page, size, Sort.by(Sort.Direction.DESC, "createdAt"));
        Query query = Query.query(criteria).with(pageable);
        
        // Exécuter la requête
        List<DocumentRequest> requests = mongoTemplate.find(query, DocumentRequest.class);
        long totalElements = mongoTemplate.count(Query.query(criteria), DocumentRequest.class);
        
        System.out.println("DocumentSyncService: Trouvé " + requests.size() + " demandes sur " + totalElements + " total");
        
        return new org.springframework.data.domain.PageImpl<>(requests, pageable, totalElements);
    }
    
    /**
     * Mettre à jour le statut d'une demande de document
     */
    public DocumentRequest updateDocumentRequestStatus(String requestId, String newStatus, 
                                                      String adminId, String adminName, String comment) {
        try {
            Optional<DocumentRequest> requestOpt = documentRequestRepository.findById(requestId);
            if (!requestOpt.isPresent()) {
                throw new RuntimeException("Demande non trouvée");
            }
            
            DocumentRequest request = requestOpt.get();
            
            // Mettre à jour le statut
            if (request.getStatus() != null) {
                request.getStatus().setCurrent(newStatus);
                
                // Mettre à jour les étapes de progression
                if (request.getStatus().getProgress() != null) {
                    for (DocumentRequest.ProgressStep step : request.getStatus().getProgress()) {
                        if (step.getStep().equals(newStatus)) {
                            step.setCompleted(true);
                            step.setDate(new Date());
                            break;
                        }
                    }
                }
            }
            
            // Assigner l'admin
            request.setAssignedAdminId(adminId);
            request.setAssignedAdminName(adminName);
            request.setUpdatedAt(new Date());
            
            // Ajouter un commentaire admin si fourni
            if (comment != null && !comment.trim().isEmpty()) {
                // Créer une structure pour les commentaires admin
                Map<String, Object> adminComment = new HashMap<>();
                adminComment.put("adminId", adminId);
                adminComment.put("adminName", adminName);
                adminComment.put("comment", comment);
                adminComment.put("date", new Date());
                
                // Ajouter à la liste des commentaires (si elle existe)
                // Note: Il faudrait ajouter un champ adminComments à DocumentRequest si nécessaire
            }
            
            return documentRequestRepository.save(request);
            
        } catch (Exception e) {
            throw new RuntimeException("Erreur lors de la mise à jour du statut: " + e.getMessage());
        }
    }
    
    /**
     * Récupérer les statistiques des demandes de documents
     */
    public Map<String, Object> getDocumentStatistics(String adminDepartment, String adminLocation, String adminRole) {
        try {
            Map<String, Object> stats = new HashMap<>();
            
            // Construire le filtre de base
            Criteria baseCriteria = new Criteria();
            if (!"SUPERADMIN".equals(adminRole)) {
                List<Criteria> conditions = new ArrayList<>();
                if (adminDepartment != null) {
                    conditions.add(Criteria.where("userDepartment").is(adminDepartment));
                }
                if (adminLocation != null) {
                    conditions.add(Criteria.where("userLocation").is(adminLocation));
                }
                if (!conditions.isEmpty()) {
                    baseCriteria = baseCriteria.andOperator(conditions.toArray(new Criteria[0]));
                }
            }
            
            // Statistiques par statut
            Arrays.asList("en attente", "en cours", "accepté", "refusé").forEach(status -> {
                Criteria statusCriteria = baseCriteria.and("status.current").is(status);
                long count = mongoTemplate.count(Query.query(statusCriteria), DocumentRequest.class);
                stats.put(status.replace(" ", "_"), count);
            });
            
            // Total
            long total = mongoTemplate.count(Query.query(baseCriteria), DocumentRequest.class);
            stats.put("total", total);
            
            // Demandes récentes (dernières 24h)
            Date yesterday = new Date(System.currentTimeMillis() - 24 * 60 * 60 * 1000);
            Criteria recentCriteria = baseCriteria.and("createdAt").gte(yesterday);
            long recentCount = mongoTemplate.count(Query.query(recentCriteria), DocumentRequest.class);
            stats.put("recent", recentCount);
            
            return stats;
            
        } catch (Exception e) {
            System.err.println("Erreur calcul statistiques documents: " + e.getMessage());
            return new HashMap<>();
        }
    }
    
    /**
     * Vérifier si un admin peut accéder à une demande de document
     */
    public boolean canAdminAccessDocumentRequest(DocumentRequest request, String adminDepartment, String adminLocation, String adminRole) {
        // SuperAdmin peut tout voir
        if ("SUPERADMIN".equals(adminRole)) {
            return true;
        }
        
        // Admin normal : vérifier département et location de l'utilisateur
        return Objects.equals(request.getUserDepartment(), adminDepartment) &&
               Objects.equals(request.getUserLocation(), adminLocation);
    }
    
    /**
     * Vérifier si un admin peut accéder à une conversation
     */
    private boolean canAdminAccessChat(Chat chat, String adminDepartment, String adminLocation, String adminRole) {
        // SuperAdmin peut tout voir
        if ("SUPERADMIN".equals(adminRole)) {
            return true;
        }
        
        // Admin normal : vérifier département et location cibles
        return Objects.equals(chat.getTargetDepartment(), adminDepartment) &&
               Objects.equals(chat.getTargetLocation(), adminLocation);
    }
}
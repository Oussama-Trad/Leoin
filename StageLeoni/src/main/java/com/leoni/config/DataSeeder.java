package com.leoni.config;

import com.leoni.models.Department;
import com.leoni.models.DocumentType;
import com.leoni.services.SuperAdminService;
import com.leoni.repositories.DepartmentRepository;
import com.leoni.repositories.DocumentTypeRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.stereotype.Component;

import java.util.Arrays;
import java.util.List;

@Component
public class DataSeeder {

    @Autowired
    private DocumentTypeRepository documentTypeRepository;
    
    @Autowired
    private DepartmentRepository departmentRepository;
    
    @Autowired
    private MongoTemplate mongoTemplate;
    
    @Autowired
    private SuperAdminService superAdminService;

    /**
     * Seed initial data after application is ready
     */
    @EventListener(ApplicationReadyEvent.class)
    public void seedInitialData() {
        seedDocumentTypes();
        seedDepartmentHierarchy();
        seedDefaultSuperAdmin();
    }
    
    /**
     * Seed initial document types
     */
    private void seedDocumentTypes() {
        try {
            // Only seed if no document types exist
            if (documentTypeRepository.count() == 0) {
                List<DocumentType> defaultDocumentTypes = Arrays.asList(
                    new DocumentType("Identity Card", "National identity card or passport"),
                    new DocumentType("Employment Contract", "Work contract and employment documents"),
                    new DocumentType("Medical Certificate", "Health and medical clearance documents"),
                    new DocumentType("Educational Certificate", "Diplomas, degrees, and educational qualifications"),
                    new DocumentType("Background Check", "Criminal background and security clearance"),
                    new DocumentType("Tax Documents", "Tax identification and related financial documents"),
                    new DocumentType("Insurance Forms", "Health, life, and work insurance documentation"),
                    new DocumentType("Emergency Contact", "Emergency contact information and forms")
                );
                
                documentTypeRepository.saveAll(defaultDocumentTypes);
                System.out.println("Seeded " + defaultDocumentTypes.size() + " default document types");
            }
        } catch (Exception e) {
            System.err.println("Error seeding document types: " + e.getMessage());
        }
    }
    
    /**
     * Seed the 3-level department hierarchy
     */
    private void seedDepartmentHierarchy() {
        try {
            // FORCE CLEAN SLATE - always reseed for now to fix structure issues
            System.out.println("Force clearing all departments to ensure new structure...");
            
            // Drop problematic indexes first
            try {
                mongoTemplate.getCollection("departments").dropIndexes();
                System.out.println("Dropped old department indexes");
            } catch (Exception e) {
                System.out.println("Could not drop indexes (may not exist): " + e.getMessage());
            }
            
            // Always clear and reseed
            departmentRepository.deleteAll();
            System.out.println("Cleared all existing departments");
            
            // Wait for delete operation to complete
            Thread.sleep(1500);
            
            // Always reseed the hierarchy
            if (true) {
                
                // Level 1: Company
                // Create simplified departments with direct location field
                List<String> departmentNames = Arrays.asList(
                    "Production",
                    "Quality Control", 
                    "Engineering",
                    "Supply Chain / Logistics",
                    "Human Resources",
                    "Finance",
                    "IT",
                    "Sales / Customer Service",
                    "R&D (Research and Development)",
                    "Maintenance",
                    "Health and Safety",
                    "Administration"
                );
                
                List<String> locations = Arrays.asList("Messadine", "Mateur", "Manzel Hayet (Monastir)");
                
                int totalDepartments = 0;
                
                // Create departments for each location using simplified structure
                for (String location : locations) {
                    for (String deptName : departmentNames) {
                        Department dept = new Department(deptName, location);
                        departmentRepository.save(dept);
                        totalDepartments++;
                    }
                }
                
                System.out.println("Seeded simplified department structure:");
                System.out.println("- " + locations.size() + " locations: " + String.join(", ", locations));
                System.out.println("- " + totalDepartments + " departments across all locations");
                
            }
        } catch (Exception e) {
            System.err.println("Error seeding department hierarchy: " + e.getMessage());
        }
    }
    
    /**
     * Create default SuperAdmin if none exists
     */
    private void seedDefaultSuperAdmin() {
        try {
            superAdminService.createDefaultSuperAdminIfNeeded();
        } catch (Exception e) {
            System.err.println("Error seeding default SuperAdmin: " + e.getMessage());
        }
    }
}

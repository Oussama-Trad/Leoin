package com.leoni.services;

import com.leoni.dto.UserDTO;
import com.leoni.models.Admin;
import com.leoni.models.Department;
import com.leoni.models.DocumentRequest;
import com.leoni.models.News;
import com.leoni.repositories.AdminRepository;
import com.leoni.repositories.DepartmentRepository;
import com.leoni.repositories.DocumentRequestRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

/**
 * Service pour gérer les droits d'accès et le filtrage des données
 * selon les rôles et permissions (Admin/SuperAdmin)
 */
@Service
public class AccessControlService {
    
    @Autowired
    private AdminRepository adminRepository;
    
    @Autowired
    private DepartmentRepository departmentRepository;
    
    @Autowired
    private DocumentRequestRepository documentRequestRepository;
    
    @Autowired
    private UserService userService;
    
    /**
     * Filtrer les employés selon les droits de l'admin
     * @param adminId ID de l'admin
     * @param adminRole Role de l'admin (ADMIN/SUPERADMIN)
     * @param locationFilter Filtre optionnel par location
     * @param departmentFilter Filtre optionnel par département
     * @param statusFilter Filtre optionnel par statut
     * @return Liste filtrée des employés
     */
    public List<UserDTO> getFilteredEmployees(String adminId, String adminRole, 
                                            String locationFilter, String departmentFilter, String statusFilter) {
        
        System.out.println("=== ACCESS CONTROL FILTERING ===");
        System.out.println("Admin ID: " + adminId + ", Role: " + adminRole);
        System.out.println("Filters - Location: " + locationFilter + ", Department: " + departmentFilter + ", Status: " + statusFilter);
        
        List<UserDTO> employees;
        
        if ("SUPERADMIN".equals(adminRole)) {
            // SuperAdmin voit tous les employés avec filtres optionnels
            employees = userService.getAllUsers();
            
            // Appliquer les filtres si fournis
            if (locationFilter != null && !locationFilter.trim().isEmpty()) {
                employees = employees.stream()
                    .filter(emp -> locationFilter.equalsIgnoreCase(emp.getLocation()))
                    .collect(Collectors.toList());
            }
            
            if (departmentFilter != null && !departmentFilter.trim().isEmpty()) {
                employees = employees.stream()
                    .filter(emp -> departmentFilter.equalsIgnoreCase(emp.getDepartment()))
                    .collect(Collectors.toList());
            }
            
            if (statusFilter != null && !statusFilter.trim().isEmpty()) {
                employees = employees.stream()
                    .filter(emp -> statusFilter.equalsIgnoreCase(emp.getStatus()))
                    .collect(Collectors.toList());
            }
            
        } else {
            // Admin normal : voir seulement les employés de son département et location
            Optional<Admin> adminOpt = adminRepository.findById(adminId);
            if (adminOpt.isPresent()) {
                Admin admin = adminOpt.get();
                String adminLocation = admin.getLocation();
                String adminDepartment = admin.getDepartment();
                
                System.out.println("Admin Department: " + adminDepartment + ", Location: " + adminLocation);
                
                // Utiliser le service existant pour filtrer par location et département
                employees = userService.getFilteredUsersByLocationAndDepartment(adminLocation, adminDepartment);
                
                // Appliquer le filtre de statut si fourni
                if (statusFilter != null && !statusFilter.trim().isEmpty()) {
                    employees = employees.stream()
                        .filter(emp -> statusFilter.equalsIgnoreCase(emp.getStatus()))
                        .collect(Collectors.toList());
                }
            } else {
                System.out.println("Admin not found, returning empty list");
                employees = List.of();
            }
        }
        
        System.out.println("Filtered employees count: " + employees.size());
        return employees;
    }
    
    /**
     * Filtrer les demandes de documents selon les droits de l'admin
     * @param adminId ID de l'admin
     * @param adminRole Role de l'admin (ADMIN/SUPERADMIN)
     * @param statusFilter Filtre optionnel par statut
     * @return Liste filtrée des demandes
     */
    public List<DocumentRequest> getFilteredDocumentRequests(String adminId, String adminRole, String statusFilter) {
        
        System.out.println("=== FILTERING DOCUMENT REQUESTS ===");
        System.out.println("Admin ID: " + adminId + ", Role: " + adminRole);
        
        List<DocumentRequest> requests;
        
        if ("SUPERADMIN".equals(adminRole)) {
            // SuperAdmin voit toutes les demandes
            if (statusFilter != null && !statusFilter.trim().isEmpty()) {
                requests = documentRequestRepository.findByStatus(statusFilter);
            } else {
                requests = documentRequestRepository.findAll();
            }
            
        } else {
            // Admin normal : voir seulement les demandes des employés de son département et location
            Optional<Admin> adminOpt = adminRepository.findById(adminId);
            if (adminOpt.isPresent()) {
                Admin admin = adminOpt.get();
                String adminLocation = admin.getLocation();
                String adminDepartment = admin.getDepartment();
                
                // Récupérer les employés du même département/location
                List<UserDTO> allowedEmployees = userService.getFilteredUsersByLocationAndDepartment(adminLocation, adminDepartment);
                List<String> allowedEmployeeIds = allowedEmployees.stream()
                    .map(UserDTO::getId)
                    .collect(Collectors.toList());
                
                // Filtrer les demandes
                if (statusFilter != null && !statusFilter.trim().isEmpty()) {
                    requests = documentRequestRepository.findByUserIdInAndStatus(allowedEmployeeIds, statusFilter);
                } else {
                    requests = documentRequestRepository.findByUserIdIn(allowedEmployeeIds);
                }
                
            } else {
                requests = List.of();
            }
        }
        
        System.out.println("Filtered document requests count: " + requests.size());
        return requests;
    }
    
    /**
     * Vérifier si un admin peut accéder aux données d'un employé spécifique
     * @param adminId ID de l'admin
     * @param adminRole Role de l'admin
     * @param employeeId ID de l'employé
     * @return true si l'accès est autorisé
     */
    public boolean canAccessEmployee(String adminId, String adminRole, String employeeId) {
        
        if ("SUPERADMIN".equals(adminRole)) {
            return true; // SuperAdmin a accès à tout
        }
        
        try {
            // Récupérer l'admin
            Optional<Admin> adminOpt = adminRepository.findById(adminId);
            if (!adminOpt.isPresent()) {
                return false;
            }
            
            Admin admin = adminOpt.get();
            String adminLocation = admin.getLocation();
            String adminDepartment = admin.getDepartment();
            
            // Récupérer l'employé
            UserDTO employee = userService.getUserById(employeeId);
            
            // Vérifier si l'employé est dans le même département et location
            return adminLocation.equalsIgnoreCase(employee.getLocation()) && 
                   adminDepartment.equalsIgnoreCase(employee.getDepartment());
                   
        } catch (Exception e) {
            System.out.println("Error checking employee access: " + e.getMessage());
            return false;
        }
    }
    
    /**
     * Vérifier si un admin peut modifier une demande de document
     * @param adminId ID de l'admin
     * @param adminRole Role de l'admin
     * @param requestId ID de la demande
     * @return true si la modification est autorisée
     */
    public boolean canModifyDocumentRequest(String adminId, String adminRole, String requestId) {
        
        if ("SUPERADMIN".equals(adminRole)) {
            return true; // SuperAdmin a accès à tout
        }
        
        try {
            // Récupérer la demande
            Optional<DocumentRequest> requestOpt = documentRequestRepository.findById(requestId);
            if (!requestOpt.isPresent()) {
                return false;
            }
            
            DocumentRequest request = requestOpt.get();
            String employeeId = request.getUserId();
            
            // Utiliser la vérification d'accès aux employés
            return canAccessEmployee(adminId, adminRole, employeeId);
            
        } catch (Exception e) {
            System.out.println("Error checking document request access: " + e.getMessage());
            return false;
        }
    }
    
    /**
     * Récupérer les options de ciblage pour un admin (locations et départements)
     * @param adminId ID de l'admin
     * @param adminRole Role de l'admin
     * @return Map contenant les options disponibles
     */
    public FilteringOptions getFilteringOptions(String adminId, String adminRole) {
        
        FilteringOptions options = new FilteringOptions();
        
        if ("SUPERADMIN".equals(adminRole)) {
            // SuperAdmin a accès à toutes les locations et départements
            List<Department> allDepartments = departmentRepository.findAll();
            
            List<String> locations = allDepartments.stream()
                .map(Department::getLocation)
                .filter(location -> location != null && !location.trim().isEmpty())
                .distinct()
                .sorted()
                .collect(Collectors.toList());
                
            List<String> departments = allDepartments.stream()
                .map(Department::getName)
                .filter(name -> name != null && !name.trim().isEmpty())
                .distinct()
                .sorted()
                .collect(Collectors.toList());
                
            options.setLocations(locations);
            options.setDepartments(departments);
            options.setCanFilterAll(true);
            
        } else {
            // Admin normal : seulement son département et location
            Optional<Admin> adminOpt = adminRepository.findById(adminId);
            if (adminOpt.isPresent()) {
                Admin admin = adminOpt.get();
                
                if (admin.getLocation() != null) {
                    options.setLocations(List.of(admin.getLocation()));
                }
                if (admin.getDepartment() != null) {
                    options.setDepartments(List.of(admin.getDepartment()));
                }
                options.setCanFilterAll(false);
            }
        }
        
        return options;
    }
    
    /**
     * Classe pour encapsuler les options de filtrage
     */
    public static class FilteringOptions {
        private List<String> locations;
        private List<String> departments;
        private boolean canFilterAll;
        
        public FilteringOptions() {
            this.locations = List.of();
            this.departments = List.of();
            this.canFilterAll = false;
        }
        
        // Getters et setters
        public List<String> getLocations() { return locations; }
        public void setLocations(List<String> locations) { this.locations = locations; }
        
        public List<String> getDepartments() { return departments; }
        public void setDepartments(List<String> departments) { this.departments = departments; }
        
        public boolean isCanFilterAll() { return canFilterAll; }
        public void setCanFilterAll(boolean canFilterAll) { this.canFilterAll = canFilterAll; }
    }
}

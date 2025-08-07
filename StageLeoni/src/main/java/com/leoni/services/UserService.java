package com.leoni.services;

import com.leoni.dto.UserDTO;
import com.leoni.exceptions.DuplicateUserException;
import com.leoni.exceptions.UserNotFoundException;
import com.leoni.models.Admin;
import com.leoni.models.Department;
import com.leoni.models.User;
import com.leoni.repositories.AdminRepository;
import com.leoni.repositories.DepartmentRepository;
import com.leoni.repositories.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
public class UserService {
    
    @Autowired
    private UserRepository userRepository;
    
    @Autowired
    private DepartmentRepository departmentRepository;
    
    @Autowired
    private AdminRepository adminRepository;
    
    /**
     * Get all users
     * @return List of UserDTO
     */
    public List<UserDTO> getAllUsers() {
        return userRepository.findAll()
                .stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }
    
    /**
     * Get user by ID
     * @param id the user ID
     * @return UserDTO
     * @throws UserNotFoundException if user not found
     */
    public UserDTO getUserById(String id) {
        User user = userRepository.findById(id)
                .orElseThrow(() -> new UserNotFoundException(id));
        return convertToDTO(user);
    }
    
    /**
     * Get user by primary email (adresse1)
     * @param adresse1 the primary email address
     * @return UserDTO
     * @throws UserNotFoundException if user not found
     */
    public UserDTO getUserByAdresse1(String adresse1) {
        User user = userRepository.findByAdresse1(adresse1)
                .orElseThrow(() -> new UserNotFoundException("adresse1", adresse1));
        return convertToDTO(user);
    }
    
    /**
     * Get user by employee ID
     * @param employeeId the employee ID
     * @return UserDTO
     * @throws UserNotFoundException if user not found
     */
    public UserDTO getUserByEmployeeId(String employeeId) {
        User user = userRepository.findByEmployeeId(employeeId)
                .orElseThrow(() -> new UserNotFoundException("employeeId", employeeId));
        return convertToDTO(user);
    }
    
    /**
     * Create a new user
     * @param userDTO the user data
     * @return created UserDTO
     * @throws DuplicateUserException if email or employee ID already exists
     */
    public UserDTO createUser(UserDTO userDTO) {
        // Check for duplicate primary email
        if (userRepository.existsByAdresse1(userDTO.getAdresse1())) {
            throw new DuplicateUserException("adresse1", userDTO.getAdresse1());
        }
        
        // Check for duplicate employee ID
        if (userRepository.existsByEmployeeId(userDTO.getEmployeeId())) {
            throw new DuplicateUserException("employeeId", userDTO.getEmployeeId());
        }
        
        User user = convertToEntity(userDTO);
        user.setCreatedAt(new Date());
        user.setUpdatedAt(new Date());
        
        User savedUser = userRepository.save(user);
        return convertToDTO(savedUser);
    }
    
    /**
     * Update an existing user
     * @param id the user ID
     * @param userDTO the updated user data
     * @return updated UserDTO
     * @throws UserNotFoundException if user not found
     * @throws DuplicateUserException if email or employee ID conflicts with another user
     */
    public UserDTO updateUser(String id, UserDTO userDTO) {
        User existingUser = userRepository.findById(id)
                .orElseThrow(() -> new UserNotFoundException(id));
        
        // Check for duplicate primary email (excluding current user)
        Optional<User> userWithAdresse1 = userRepository.findByAdresse1(userDTO.getAdresse1());
        if (userWithAdresse1.isPresent() && !userWithAdresse1.get().getId().equals(id)) {
            throw new DuplicateUserException("adresse1", userDTO.getAdresse1());
        }
        
        // Check for duplicate employee ID (excluding current user)
        Optional<User> userWithEmployeeId = userRepository.findByEmployeeId(userDTO.getEmployeeId());
        if (userWithEmployeeId.isPresent() && !userWithEmployeeId.get().getId().equals(id)) {
            throw new DuplicateUserException("employeeId", userDTO.getEmployeeId());
        }
        
        // Update fields
        existingUser.setFirstName(userDTO.getFirstName());
        existingUser.setLastName(userDTO.getLastName());
        existingUser.setAdresse1(userDTO.getAdresse1());
        existingUser.setAdresse2(userDTO.getAdresse2());
        existingUser.setPhoneNumber(userDTO.getPhoneNumber());
        existingUser.setEmployeeId(userDTO.getEmployeeId());
        existingUser.setDepartmentId(userDTO.getDepartmentId());
        existingUser.setPosition(userDTO.getPosition() != null ? userDTO.getPosition() : "Non spécifié");
        
        // Update location field if provided
        if (userDTO.getLocationName() != null && !userDTO.getLocationName().trim().isEmpty()) {
            existingUser.setLocation(userDTO.getLocationName());
        }
        
        existingUser.setUpdatedAt(new Date());
        
        User savedUser = userRepository.save(existingUser);
        return convertToDTO(savedUser);
    }
    
    /**
     * Delete a user
     * @param id the user ID
     * @throws UserNotFoundException if user not found
     */
    public void deleteUser(String id) {
        if (!userRepository.existsById(id)) {
            throw new UserNotFoundException(id);
        }
        userRepository.deleteById(id);
    }
    
    /**
     * Search users by name
     * @param searchTerm the search term
     * @return List of matching UserDTO
     */
    public List<UserDTO> searchUsersByName(String searchTerm) {
        return userRepository.searchByName(searchTerm)
                .stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }
    
    /**
     * Get users by department ID
     * @param departmentId the department ID
     * @return List of UserDTO
     */
    public List<UserDTO> getUsersByDepartmentId(String departmentId) {
        return userRepository.findByDepartmentId(departmentId)
                .stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }
    
    /**
     * Get users by position
     * @param position the position name
     * @return List of UserDTO
     */
    public List<UserDTO> getUsersByPosition(String position) {
        return userRepository.findByPosition(position)
                .stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }
    
    /**
     * Convert User entity to UserDTO
     * @param user the User entity
     * @return UserDTO
     */
    private UserDTO convertToDTO(User user) {
        UserDTO dto = new UserDTO();
        dto.setId(user.getId());
        dto.setFirstName(user.getFirstName() != null ? user.getFirstName() : "");
        dto.setLastName(user.getLastName() != null ? user.getLastName() : "");
        
        // Map email fields correctly - use proper DTO field names
        String primaryEmail = null;
        String secondaryEmail = null;
        
        if (user.getEmail() != null && !user.getEmail().trim().isEmpty()) {
            primaryEmail = user.getEmail();
        } else if (user.getAdresse1() != null && !user.getAdresse1().trim().isEmpty()) {
            primaryEmail = user.getAdresse1();
        }
        
        if (user.getParentalEmail() != null && !user.getParentalEmail().trim().isEmpty()) {
            secondaryEmail = user.getParentalEmail();
        } else if (user.getAdresse2() != null && !user.getAdresse2().trim().isEmpty()) {
            secondaryEmail = user.getAdresse2();
        }
        
        // Set the correct DTO fields for emails
        dto.setEmail(primaryEmail != null ? primaryEmail : "");
        dto.setParentalEmail(secondaryEmail != null ? secondaryEmail : "");
        dto.setAdresse1(primaryEmail != null ? primaryEmail : "");
        dto.setAdresse2(secondaryEmail != null ? secondaryEmail : "");
        
        // Map phone fields correctly
        String primaryPhoneNumber = null;
        String secondaryPhoneNumber = null;
        
        if (user.getPhoneNumber() != null && !user.getPhoneNumber().trim().isEmpty()) {
            primaryPhoneNumber = user.getPhoneNumber();
        }
        
        if (user.getParentalPhoneNumber() != null && !user.getParentalPhoneNumber().trim().isEmpty()) {
            secondaryPhoneNumber = user.getParentalPhoneNumber();
        }
        
        // Set the correct DTO fields for phone numbers
        dto.setPhoneNumber(primaryPhoneNumber != null ? primaryPhoneNumber : "");
        dto.setParentalPhoneNumber(secondaryPhoneNumber != null ? secondaryPhoneNumber : "");
        
        dto.setEmployeeId(user.getEmployeeId() != null ? user.getEmployeeId() : "");
        
        // Set department information
        dto.setDepartmentId(user.getDepartmentId());
        if (user.getDepartmentId() != null) {
            Optional<Department> department = departmentRepository.findById(user.getDepartmentId());
            if (department.isPresent()) {
                Department dept = department.get();
                dto.setDepartmentName(dept.getName() != null ? dept.getName() : "");
                
                // Get location information - prioritize new structure
                if (dept.getLocation() != null && !dept.getLocation().trim().isEmpty()) {
                    // Use new location field from department
                    dto.setLocationName(dept.getLocation());
                } else {
                    // Fallback to user's direct location field
                    dto.setLocationName(user.getLocation() != null ? user.getLocation() : "");
                }
            } else {
                // Department ID not found, use direct user fields
                dto.setDepartmentName(user.getDepartment() != null ? user.getDepartment() : "");
                dto.setLocationName(user.getLocation() != null ? user.getLocation() : "");
            }
        } else {
            // No departmentId, use direct user fields
            dto.setDepartmentName(user.getDepartment() != null ? user.getDepartment() : "");
            dto.setLocationName(user.getLocation() != null ? user.getLocation() : "");
        }
        
        dto.setPosition(user.getPosition() != null ? user.getPosition() : "Non spécifié");
        dto.setStatus(user.getStatus() != null ? user.getStatus() : "approved");
        dto.setDocumentRequestIds(user.getDocumentRequestIds() != null ? user.getDocumentRequestIds() : new ArrayList<>());
        dto.setCreatedAt(user.getCreatedAt());
        dto.setUpdatedAt(user.getUpdatedAt());
        return dto;
    }
    
    /**
     * Convert UserDTO to User entity
     * @param userDTO the UserDTO
     * @return User entity
     */
    private User convertToEntity(UserDTO userDTO) {
        User user = new User();
        user.setFirstName(userDTO.getFirstName());
        user.setLastName(userDTO.getLastName());
        user.setAdresse1(userDTO.getAdresse1());
        user.setAdresse2(userDTO.getAdresse2());
        user.setPhoneNumber(userDTO.getPhoneNumber());
        user.setEmployeeId(userDTO.getEmployeeId());
        user.setDepartmentId(userDTO.getDepartmentId());
        user.setPosition(userDTO.getPosition() != null ? userDTO.getPosition() : "Non spécifié");
        user.setStatus(userDTO.getStatus() != null ? userDTO.getStatus() : "pending");
        // Map location and department fields
        user.setLocation(userDTO.getLocation());
        user.setDepartment(userDTO.getDepartment());
        user.setLocationRef(userDTO.getLocationRef());
        user.setDepartmentRef(userDTO.getDepartmentRef());
        return user;
    }

    /**
     * Get all pending users (status = "pending")
     * @return List of pending UserDTO
     */
    public List<UserDTO> getPendingUsers() {
        return userRepository.findByStatus("pending")
                .stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    /**
     * Approve a pending user (change status from "pending" to "approved")
     * @param userId the user ID
     * @return updated UserDTO
     * @throws UserNotFoundException if user not found
     */
    public UserDTO approveUser(String userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new UserNotFoundException(userId));
        
        if (!"pending".equals(user.getStatus())) {
            throw new IllegalStateException("User is not in pending status");
        }
        
        user.setStatus("approved");
        user.setUpdatedAt(new Date());
        
        User savedUser = userRepository.save(user);
        return convertToDTO(savedUser);
    }

    /**
     * Reject a pending user (delete their account)
     * @param userId the user ID
     * @throws UserNotFoundException if user not found
     */
    public void rejectUser(String userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new UserNotFoundException(userId));
        
        if (!"pending".equals(user.getStatus())) {
            throw new IllegalStateException("User is not in pending status");
        }
        
        userRepository.deleteById(userId);
    }
    
    /**
     * Get users filtered by admin's department
     * Simple rule: Admin only sees employees with exactly the same departmentId
     * @param adminDepartmentId the admin's department ID
     * @return List of UserDTO with same department as admin
     */
    public List<UserDTO> getFilteredUsersByAdminDepartment(String adminDepartmentId) {
        if (adminDepartmentId == null || adminDepartmentId.isEmpty()) {
            return List.of(); // Empty list if no department assigned
        }
        
        // Simple filtering: get all users with the same departmentId as the admin
        List<User> filteredUsers = userRepository.findByDepartmentId(adminDepartmentId);
        
        return filteredUsers.stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }
    
    /**
     * Get users filtered by admin's location and department strings
     * This works with the new simplified department structure where departments have direct location field
     * Filtre les utilisateurs selon les critères suivants :
     * - Même location que l'admin
     * - Même department que l'admin
     * @param adminLocation the admin's location string
     * @param adminDepartment the admin's department string  
     * @return List of UserDTO with matching location and department
     */
    public List<UserDTO> getFilteredUsersByLocationAndDepartment(String adminLocation, String adminDepartment) {
        System.out.println("=== FILTERING BY LOCATION AND DEPARTMENT (New Structure) ===");
        System.out.println("Admin Location: " + adminLocation);
        System.out.println("Admin Department: " + adminDepartment);
        
        if (adminLocation == null || adminLocation.trim().isEmpty()) {
            System.out.println("Admin location is null/empty - returning empty list");
            return List.of(); // Empty list if no location assigned
        }
        
        // Get all users and filter by location and department
        List<User> allUsers = userRepository.findAll();
        System.out.println("Total users in database: " + allUsers.size());
        
        List<User> filteredUsers = allUsers.stream()
                .filter(user -> {
                    // Use direct location and department fields from user
                    String userLocation = user.getLocation();
                    String userDepartment = user.getDepartment();
                    
                    // If user has departmentId, get location from department (new structure only)
                    if (user.getDepartmentId() != null && !user.getDepartmentId().trim().isEmpty()) {
                        Optional<Department> dept = departmentRepository.findById(user.getDepartmentId());
                        if (dept.isPresent()) {
                            Department department = dept.get();
                            // Use new location field from department
                            if (department.getLocation() != null && !department.getLocation().trim().isEmpty()) {
                                userLocation = department.getLocation();
                                userDepartment = department.getName();
                            }
                        }
                    }
                    
                    boolean locationMatch = adminLocation.equalsIgnoreCase(userLocation);
                    boolean departmentMatch = adminDepartment == null || 
                                            adminDepartment.trim().isEmpty() || 
                                            adminDepartment.equalsIgnoreCase(userDepartment);
                    
                    System.out.println("User " + user.getEmployeeId() + 
                                     " - Location: '" + userLocation + "'" +
                                     " - Department: '" + userDepartment + "'" +
                                     " - LocationMatch: " + locationMatch +
                                     " - DepartmentMatch: " + departmentMatch);
                    
                    return locationMatch && departmentMatch;
                })
                .collect(Collectors.toList());
        
        System.out.println("Filtered users count: " + filteredUsers.size());
        
        return filteredUsers.stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }
    
    /**
     * Get users filtered by admin username (gets admin's department and location, then filters users)
     * @param adminUsername the admin's username
     * @return List of UserDTO with same location and department as admin
     */
    public List<UserDTO> getFilteredUsersByAdminUsername(String adminUsername) {
        System.out.println("=== FILTERING BY ADMIN USERNAME ===");
        System.out.println("Admin Username: " + adminUsername);
        
        if (adminUsername == null || adminUsername.trim().isEmpty()) {
            System.out.println("Admin username is null/empty - returning empty list");
            return List.of();
        }
        
        // Find the admin by username
        Optional<Admin> adminOpt = adminRepository.findByUsername(adminUsername);
        if (!adminOpt.isPresent()) {
            System.out.println("Admin not found with username: " + adminUsername);
            return List.of();
        }
        
        Admin admin = adminOpt.get();
        String adminLocation = admin.getLocation();
        String adminDepartment = admin.getDepartment();
        
        System.out.println("Found admin - Location: '" + adminLocation + "', Department: '" + adminDepartment + "'");
        
        // Use existing filtering method
        return getFilteredUsersByLocationAndDepartment(adminLocation, adminDepartment);
    }
    
    /**
     * Get users based on role - for admins: filtered by their location/department, for superadmins: all users with optional filters
     * @param userRole the role of the requesting user (ADMIN or SUPERADMIN)
     * @param userId the ID of the requesting user
     * @param filterLocation optional location filter (mainly for superadmin)
     * @param filterDepartment optional department filter (mainly for superadmin)
     * @param filterStatus optional status filter
     * @return List of UserDTO based on role and filters
     */
    public List<UserDTO> getUsersByRole(String userRole, String userId, String filterLocation, String filterDepartment, String filterStatus) {
        System.out.println("=== FILTERING BY ROLE ===");
        System.out.println("User Role: " + userRole + ", User ID: " + userId);
        System.out.println("Filters - Location: " + filterLocation + ", Department: " + filterDepartment + ", Status: " + filterStatus);
        
        List<UserDTO> users;
        
        if ("SUPERADMIN".equals(userRole)) {
            // SuperAdmin sees all users with optional filtering
            users = getAllUsers();
            
            // Apply filters if provided
            if (filterLocation != null && !filterLocation.trim().isEmpty()) {
                users = users.stream()
                    .filter(user -> filterLocation.equalsIgnoreCase(user.getLocation()))
                    .collect(Collectors.toList());
            }
            
            if (filterDepartment != null && !filterDepartment.trim().isEmpty()) {
                users = users.stream()
                    .filter(user -> filterDepartment.equalsIgnoreCase(user.getDepartment()))
                    .collect(Collectors.toList());
            }
            
            if (filterStatus != null && !filterStatus.trim().isEmpty()) {
                users = users.stream()
                    .filter(user -> filterStatus.equalsIgnoreCase(user.getStatus()))
                    .collect(Collectors.toList());
            }
            
        } else {
            // Admin sees only users from their location and department
            Optional<Admin> adminOpt = adminRepository.findById(userId);
            if (adminOpt.isPresent()) {
                Admin admin = adminOpt.get();
                users = getFilteredUsersByLocationAndDepartment(admin.getLocation(), admin.getDepartment());
                
                // Apply status filter if provided
                if (filterStatus != null && !filterStatus.trim().isEmpty()) {
                    users = users.stream()
                        .filter(user -> filterStatus.equalsIgnoreCase(user.getStatus()))
                        .collect(Collectors.toList());
                }
            } else {
                System.out.println("Admin not found with ID: " + userId);
                users = List.of();
            }
        }
        
        System.out.println("Returning " + users.size() + " users");
        return users;
    }
    
    /**
     * Get all users for superadmin with optional filters
     * @param location optional location filter
     * @param department optional department filter
     * @param status optional status filter
     * @return List of filtered UserDTO
     */
    public List<UserDTO> getAllUsersWithFilters(String location, String department, String status) {
        List<UserDTO> users = getAllUsers();
        
        if (location != null && !location.trim().isEmpty()) {
            users = users.stream()
                .filter(user -> location.equalsIgnoreCase(user.getLocation()))
                .collect(Collectors.toList());
        }
        
        if (department != null && !department.trim().isEmpty()) {
            users = users.stream()
                .filter(user -> department.equalsIgnoreCase(user.getDepartment()))
                .collect(Collectors.toList());
        }
        
        if (status != null && !status.trim().isEmpty()) {
            users = users.stream()
                .filter(user -> status.equalsIgnoreCase(user.getStatus()))
                .collect(Collectors.toList());
        }
        
        return users;
    }

    /**
     * Get departments by location name (new simplified structure)
     * @param locationName the location name
     * @return List of departments in that location
     */
    public List<Department> getDepartmentsByLocation(String locationName) {
        return departmentRepository.findAll().stream()
                .filter(dept -> locationName.equalsIgnoreCase(dept.getLocation()))
                .collect(Collectors.toList());
    }
    
    /**
     * Get all unique locations from departments (new simplified structure)
     * @return List of unique location names
     */
    public List<String> getAllLocations() {
        return departmentRepository.findAll().stream()
                .map(Department::getLocation)
                .filter(location -> location != null && !location.trim().isEmpty())
                .distinct()
                .sorted()
                .collect(Collectors.toList());
    }
    
    /**
     * Get all unique departments
     * @return List of unique department names
     */
    public List<String> getAllDepartments() {
        return departmentRepository.findAll().stream()
                .map(Department::getName)
                .filter(name -> name != null && !name.trim().isEmpty())
                .distinct()
                .sorted()
                .collect(Collectors.toList());
    }
}
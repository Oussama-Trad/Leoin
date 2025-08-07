package com.leoni.dto;

import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

import java.util.Date;
import java.util.List;

@Data
@NoArgsConstructor
public class UserDTO {
    
    private String id;
    
    private String firstName;
    private String lastName;
    private String email; // Primary email address (matching MongoDB field)
    private String parentalEmail; // Parental email address (matching MongoDB field)
    private String adresse1; // Alternative email field (backward compatibility)
    private String adresse2; // Alternative parental email field (backward compatibility)
    private String phoneNumber;
    private String parentalPhoneNumber;
    private String employeeId;
    
    private String department; // Department name as string
    private String departmentRef; // Reference to Department ObjectId
    private String departmentId; // Department ID field
    private String location; // Location name as string
    private String locationRef; // Reference to Location ObjectId
    private String departmentName; // For display purposes (backward compatibility)
    private String locationName; // For display purposes
    private String companyName; // For display purposes
    private String position;
    private String status;
    
    private List<String> documentRequestIds;
    
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private Date createdAt;
    
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private Date updatedAt;
    
    
    // Helper method to get full name
    public String getFullName() {
        return firstName + " " + lastName;
    }
    
    // Helper methods for backward compatibility
    public String getDepartmentName() {
        return departmentName != null ? departmentName : department;
    }
    
    public String getLocationName() {
        return locationName != null ? locationName : location;
    }
    
    // Getters for email fields (backward compatibility)
    public String getAdresse1() {
        return adresse1 != null ? adresse1 : email;
    }
    
    public void setAdresse1(String adresse1) {
        this.adresse1 = adresse1;
    }
    
    public String getAdresse2() {
        return adresse2 != null ? adresse2 : parentalEmail;
    }
    
    public void setAdresse2(String adresse2) {
        this.adresse2 = adresse2;
    }
    
    public String getDepartmentId() {
        return departmentId != null ? departmentId : departmentRef;
    }
    
    public void setDepartmentId(String departmentId) {
        this.departmentId = departmentId;
    }
}
package com.leoni.models;

import lombok.Data;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

@Data
@Document(collection = "departments")
public class Department {
    @Id
    private String id;
    
    private String name;
    private String location;
    
    public Department() {
    }
    
    public Department(String name, String location) {
        this.name = name;
        this.location = location;
    }
}

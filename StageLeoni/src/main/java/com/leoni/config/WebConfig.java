package com.leoni.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        // Configure static resource handler for uploaded files
        registry.addResourceHandler("/uploads/**")
                .addResourceLocations("file:uploads/");
        
        // Keep existing static resources configuration
        registry.addResourceHandler("/static/**")
                .addResourceLocations("classpath:/static/");
    }
}

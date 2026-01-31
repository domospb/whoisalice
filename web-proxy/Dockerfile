# Start from official nginx image (alpine version - smallest Linux distro)
FROM nginx:alpine

# Remove the default nginx configuration file
# We'll replace it with our custom config
RUN rm /etc/nginx/nginx.conf

# Copy our custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Document that this container listens on port 80
EXPOSE 80

# Start nginx in foreground mode
# -g "daemon off;" - keeps nginx in foreground so container doesn't exit
CMD ["nginx", "-g", "daemon off;"]

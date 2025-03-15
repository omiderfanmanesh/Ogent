FROM ubuntu:22.04

# Install OpenSSH Server and other utilities
RUN apt-get update && \
    apt-get install -y openssh-server sudo curl wget nano && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create SSH directory
RUN mkdir /var/run/sshd

# Set up SSH user
ARG SSH_USER=ubuntu
ARG SSH_PASSWORD=password

# Create user and set password
RUN useradd -m -s /bin/bash ${SSH_USER} && \
    echo "${SSH_USER}:${SSH_PASSWORD}" | chpasswd && \
    adduser ${SSH_USER} sudo && \
    echo "${SSH_USER} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${SSH_USER}

# SSH login fix
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

# Create a test directory with some files
RUN mkdir -p /home/${SSH_USER}/test && \
    echo "Hello from Ubuntu target" > /home/${SSH_USER}/test/hello.txt && \
    chown -R ${SSH_USER}:${SSH_USER} /home/${SSH_USER}/test

# Expose SSH port
EXPOSE 22

# Add health check
HEALTHCHECK --interval=5s --timeout=3s --retries=3 \
    CMD pgrep sshd || exit 1

# Start SSH service
CMD ["/usr/sbin/sshd", "-D"] 
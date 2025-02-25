# Container for comparing projects
# Use
#  podman build --ulimit nofile=65536:65536 -t diffkemp-automation .
#  ulimit is set because of npm

FROM docker://nixos/nix
RUN echo "experimental-features = nix-command flakes" >> /etc/nix/nix.conf

RUN git clone https://github.com/diffkemp/diffkemp /diffkemp
COPY files /runner

# Caching dependencies
RUN nix develop /runner/ --command echo 'Nix dependencies downloaded'
RUN /runner/build_diffkemp.sh && rm -rf /diffkemp/build

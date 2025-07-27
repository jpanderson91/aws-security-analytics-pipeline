# ============================================================================
# CAP Demo - Network Infrastructure Configuration
# ============================================================================
# Purpose: Multi-AZ VPC design for enterprise MSK Kafka deployment
#
# This network architecture implements AWS best practices for:
# - High availability across 3 availability zones
# - Security through private/public subnet separation
# - Scalability with proper CIDR allocation
# - Cost optimization with shared NAT gateways
#
# Network Design Pattern:
# - Public subnets: NAT gateways, load balancers, bastion hosts
# - Private subnets: MSK brokers, application servers, databases
# - Internet Gateway: Public subnet internet access
# - NAT Gateways: Private subnet outbound internet access (updates, etc.)
# ============================================================================

# ============================================================================
# VPC - Virtual Private Cloud Foundation
# ============================================================================

# Main VPC for the entire CAP demo environment
# Provides network isolation and serves as the foundation for all resources
resource "aws_vpc" "cap_demo" {
  cidr_block           = var.vpc_cidr             # 10.0.0.0/16 = 65,536 IP addresses
  enable_dns_hostnames = var.enable_dns_hostnames # Required for MSK broker hostname resolution
  enable_dns_support   = var.enable_dns_support   # Required for AWS service integration

  # Comprehensive tagging for resource management and cost allocation
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-vpc" # cap-demo-dev-vpc
    Type = "Network"                  # Resource type classification
  })
}

# ============================================================================
# Internet Gateway - Public Internet Access
# ============================================================================

# Internet Gateway provides public subnet access to the internet
# Required for NAT gateway functionality and any public-facing resources
resource "aws_internet_gateway" "cap_demo" {
  vpc_id = aws_vpc.cap_demo.id # Attach to our VPC

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-igw" # cap-demo-dev-igw
    Type = "Network"
  })
}

# ============================================================================
# Private Subnets - MSK Kafka Broker Placement
# ============================================================================

# Private subnets for MSK brokers - one subnet per availability zone
# MSK requires multi-AZ deployment for high availability and fault tolerance
# Private placement ensures brokers are not directly accessible from internet
resource "aws_subnet" "private" {
  count = length(local.azs) # Create 3 subnets (one per AZ)

  vpc_id = aws_vpc.cap_demo.id
  # CIDR calculation: 10.0.10.0/24, 10.0.11.0/24, 10.0.12.0/24
  # Each subnet gets 256 IP addresses (254 usable)
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 10)
  availability_zone = local.azs[count.index] # us-east-1a, us-east-1b, us-east-1c

  # Private subnets do NOT auto-assign public IPs for security
  # map_public_ip_on_launch = false (default)

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-private-${count.index + 1}" # cap-demo-dev-private-1
    Type = "Private"                                         # Subnet classification
    AZ   = local.azs[count.index]                            # AZ identification
  })
}

# ============================================================================
# Public Subnets - NAT Gateway and Bastion Host Placement
# ============================================================================

# Public subnets for NAT gateways and any public-facing infrastructure
# These provide internet access for private subnet resources through NAT
resource "aws_subnet" "public" {
  count = length(local.azs) # Create 3 subnets (one per AZ)

  vpc_id = aws_vpc.cap_demo.id
  # CIDR calculation: 10.0.20.0/24, 10.0.21.0/24, 10.0.22.0/24
  # Separate from private subnets to avoid IP conflicts
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index + 20)
  availability_zone       = local.azs[count.index]
  map_public_ip_on_launch = true # Auto-assign public IPs for resources

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-public-${count.index + 1}" # cap-demo-dev-public-1
    Type = "Public"                                         # Subnet classification
    AZ   = local.azs[count.index]                           # AZ identification
  })
}

# ============================================================================
# Elastic IPs - Static IP Addresses for NAT Gateways
# ============================================================================

# Elastic IPs for NAT gateways provide consistent outbound IP addresses
# Important for whitelisting and external service integration
# Using single NAT gateway for demo cost optimization
resource "aws_eip" "nat" {
  count = 1 # Single NAT gateway for demo

  domain = "vpc" # VPC-allocated EIP (not EC2-Classic)

  # EIPs must be created after Internet Gateway for proper routing
  depends_on = [aws_internet_gateway.cap_demo]

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-nat-eip-${count.index + 1}" # cap-demo-dev-nat-eip-1
    Type = "Network"
  })
}

# ============================================================================
# NAT Gateways - Private Subnet Internet Access
# ============================================================================

# NAT gateways provide outbound internet access for private subnet resources
# Essential for MSK brokers to download updates and communicate with AWS services
# Using single NAT gateway for demo cost optimization
resource "aws_nat_gateway" "cap_demo" {
  count = 1 # Single NAT gateway for demo

  allocation_id = aws_eip.nat[0].id       # Associate with first EIP
  subnet_id     = aws_subnet.public[0].id # Place in first public subnet

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-nat-${count.index + 1}" # cap-demo-dev-nat-1
    Type = "Network"
  })

  # NAT gateways require Internet Gateway to be fully operational
  depends_on = [aws_internet_gateway.cap_demo]
}

# ============================================================================
# Route Tables - Traffic Routing Configuration
# ============================================================================

# Public route table - directs internet traffic through Internet Gateway
# All public subnets share this single route table for simplicity
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.cap_demo.id

  # Default route: send all traffic (0.0.0.0/0) to Internet Gateway
  # This enables internet access for public subnet resources
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.cap_demo.id
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-public-rt" # cap-demo-dev-public-rt
    Type = "Network"
  })
}

# Private route tables - one per AZ for independent NAT gateway routing
# Separate route tables ensure each AZ uses its local NAT gateway
# This provides fault isolation - if one NAT gateway fails, others unaffected
resource "aws_route_table" "private" {
  count = length(local.azs) # One route table per AZ

  vpc_id = aws_vpc.cap_demo.id

  # Default route: send all traffic to the single NAT gateway
  # This provides internet access while maintaining private subnet security
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.cap_demo[0].id
  }

  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-private-rt-${count.index + 1}" # cap-demo-dev-private-rt-1
    Type = "Network"
    AZ   = local.azs[count.index]
  })
}

# ============================================================================
# Route Table Associations - Connect Subnets to Route Tables
# ============================================================================

# Associate all public subnets with the single public route table
# This configuration enables internet access for all public subnet resources
resource "aws_route_table_association" "public" {
  count = length(aws_subnet.public) # Associate all public subnets

  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# Associate each private subnet with its AZ-specific route table
# This ensures each private subnet uses its local NAT gateway for internet access
resource "aws_route_table_association" "private" {
  count = length(aws_subnet.private) # Associate all private subnets

  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id # AZ-specific route table
}

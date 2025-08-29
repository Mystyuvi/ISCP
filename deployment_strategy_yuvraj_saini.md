# Deployment Strategy – Project Guardian 2.0

## Objective
Deploy a **PII Detection & Redaction Service** to prevent sensitive customer data from leaking through APIs, logs, or unmonitored endpoints.  
The solution must be **low-latency, scalable, and easy to integrate** into Flixkart’s infrastructure.

---

## Recommended Deployment

### 1. API Gateway Plugin (Primary Layer)
- Place the PII Sanitizer at the **Ingress Gateway**.  
- All requests and responses are inspected before reaching internal services.  
- PII is masked **before logging, monitoring, or storage**.

### 2. Sidecar Microservice (Secondary Layer)
- Run the sanitizer as a **sidecar container** alongside application pods.  
- Ensures **internal logs, background jobs, and service-to-service calls** are also protected.  
- Uses **regex + NER hybrid detection** for accuracy and speed.

### 3. Central Policy Manager
- Stores and updates **regex rules, ML models, and masking policies**.  
- Sidecars and the gateway fetch updates dynamically (via config maps or REST API).  

---

## Data Flow
1. **Client Request → API Gateway**  
2. **Gateway Plugin (PII Sanitizer)** checks payloads/logs.  
3. **PII masked** before passing data downstream.  
4. **Only redacted data** is stored in logs and databases.  

---

## Benefits
- **Scalable:** Works natively with Kubernetes (sidecars or DaemonSets).  
- **Low latency:** Regex-based redaction adds <10ms overhead.  
- **Cost-effective:** No major changes to existing applications.  
- **Compliant:** Meets GDPR, PDPB, and other data protection laws.  

---

## Alternatives Considered
- **Browser Extension:** Limited to end-users, not scalable.  
- **App-Layer Code Changes:** High engineering cost.  
- **Database Masking:** Too late, as leaks may already occur upstream.  

---

## Final Choice
**API Gateway Plugin + Sidecar Microservice (Hybrid Approach)**  
- Gateway layer: stops PII leaks at the **edge**.  
- Sidecar layer: protects **internal applications and logs**.  
- Together, they provide **defense-in-depth** against PII exposure.  

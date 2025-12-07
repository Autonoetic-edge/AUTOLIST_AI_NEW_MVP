# AutoList AI - Integration Test Checklist

## Phase 1 Acceptance Criteria

This checklist covers all integration tests and acceptance criteria for Phase 1 of the AutoList AI MVP.

---

## 1. End-to-End Test: Single Product Mapping

### Prerequisites
- [ ] MongoDB is running and accessible
- [ ] Backend server is running on port 8000
- [ ] Frontend is running on port 5173
- [ ] Test Shopify credentials are configured (or use mock mode)
- [ ] Claude API key is configured (or use mock mode)

### Test Steps

#### 1.1 User Authentication
- [ ] Navigate to login page (`/login`)
- [ ] Attempt login with invalid credentials → Should show error message
- [ ] Login with valid credentials → Should redirect to dashboard
- [ ] Verify JWT token is stored in localStorage
- [ ] Verify protected routes redirect to login when unauthenticated

#### 1.2 Shopify Store Connection
- [ ] Navigate to Connect page (`/connect`)
- [ ] Enter shop domain: `test-store.myshopify.com`
- [ ] Enter access token
- [ ] Click "Connect Store"
- [ ] Verify success message is displayed
- [ ] Verify store connection is persisted

#### 1.3 Product Sync
- [ ] Click "Sync Products" button
- [ ] Verify loading state is displayed
- [ ] Verify at least 2 sample products are synced
- [ ] Verify products appear in Products page
- [ ] Verify product data includes: title, description, variants, images

#### 1.4 Template Selection and Mapping Initiation
- [ ] Navigate to Products page (`/products`)
- [ ] Select one product by clicking checkbox
- [ ] Select template: "Amazon - Shirt"
- [ ] Click "Map 1 Product"
- [ ] Verify mapping job is created
- [ ] Verify redirect to Mapping Preview page

#### 1.5 Mapping Preview and Editing
- [ ] Verify all schema fields are displayed
- [ ] Verify confidence badges show correct colors:
  - [ ] Green for ≥80% confidence
  - [ ] Yellow for 50-79% confidence
  - [ ] Red for <50% confidence
- [ ] Click edit icon on a field
- [ ] Modify the value
- [ ] Click save
- [ ] Verify confidence is updated to 100%
- [ ] Click "Approve All Suggested"
- [ ] Verify low-confidence fields are updated

#### 1.6 Export and Download
- [ ] Click "Save & Download"
- [ ] Verify XLSX file is downloaded
- [ ] Open XLSX in Excel or Google Sheets
- [ ] Verify columns match schema column order (by col_index)
- [ ] Verify header row contains correct field names
- [ ] Verify data row contains mapped values
- [ ] Verify confidence coloring is applied (if enabled)

---

## 2. Validation Scenarios

### 2.1 Missing Required Fields
- [ ] Create mapping with `brand` field set to null
- [ ] Attempt to export
- [ ] Verify validation error: "Required field 'brand' is missing"
- [ ] Verify job status is "needs_user_input"

### 2.2 Enum Mismatch
- [ ] Create mapping with `fabric` = "Wool" (not in enum)
- [ ] Verify validation error about enum values
- [ ] Edit field to valid enum value: "Cotton"
- [ ] Verify validation passes

### 2.3 Type Validation
- [ ] Create mapping with `price` = "not-a-number"
- [ ] Verify validation error about invalid type
- [ ] Edit field to valid value: "29.99"
- [ ] Verify validation passes

### 2.4 Low Confidence Warning
- [ ] Create mapping where required field has confidence < 0.5
- [ ] Verify export validation warns about low confidence
- [ ] Edit field manually
- [ ] Verify confidence is updated to 1.0
- [ ] Verify export validation passes

---

## 3. UI Acceptance Tests

### 3.1 Login Page
- [ ] Modern, clean design with proper spacing
- [ ] Logo and title displayed
- [ ] Tab switching between Sign In / Create Account
- [ ] Form validation feedback
- [ ] Loading state during submission
- [ ] Demo login button works

### 3.2 Dashboard Page
- [ ] Stat cards show correct values
- [ ] Auto-fill rate progress circle renders
- [ ] Recent activity list loads
- [ ] Quick action cards are clickable
- [ ] Responsive layout on mobile

### 3.3 Products Page
- [ ] Product table displays all synced products
- [ ] Checkboxes work for selection
- [ ] Select All functionality works
- [ ] Template dropdown shows available schemas
- [ ] "Map N Products" button state updates correctly
- [ ] Empty state shown when no products

### 3.4 Mapping Preview Page
- [ ] All mapped fields displayed in table
- [ ] Confidence badges color-coded correctly
- [ ] Inline editing works
- [ ] Approve All button updates all fields
- [ ] Stats cards show correct counts
- [ ] Legend explains color coding

### 3.5 Download Page
- [ ] Ready jobs listed in table
- [ ] Batch selection works
- [ ] Single download works
- [ ] Batch download works
- [ ] Auto-fill rate progress bar displays correctly

---

## 4. API Endpoint Tests

### 4.1 Authentication Endpoints
```bash
# Register new user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","name":"Test User"}'
# Expected: 201 Created with user object

# Login
curl -X POST http://localhost:8000/api/auth/token \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
# Expected: 200 OK with access_token

# Get current user (with token)
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <token>"
# Expected: 200 OK with user object
```

### 4.2 Shopify Endpoints
```bash
# Connect store
curl -X POST http://localhost:8000/api/shopify/connect \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"shop_domain":"test.myshopify.com","access_token":"shpat_xxx"}'
# Expected: 200 OK with success message

# Sync products
curl -X POST http://localhost:8000/api/shopify/sync-products \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"shop_domain":"test.myshopify.com"}'
# Expected: 200 OK with products array
```

### 4.3 Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy","version":"1.0.0"}
```

---

## 5. Load Test Plan (20 Concurrent Users)

### Test Configuration
- **Tool**: Apache JMeter or k6
- **Duration**: 5 minutes
- **Ramp-up**: 30 seconds
- **Concurrent Users**: 20

### Scenarios to Test

#### 5.1 Login Load Test
- **Endpoint**: POST `/api/auth/token`
- **Target**: 100 requests/second
- **Success Criteria**:
  - [ ] 95th percentile response time < 500ms
  - [ ] Error rate < 1%

#### 5.2 Product Listing Load Test
- **Endpoint**: GET `/api/shopify/products`
- **Target**: 50 requests/second
- **Success Criteria**:
  - [ ] 95th percentile response time < 1s
  - [ ] Error rate < 1%

#### 5.3 Mapping Job Creation Load Test
- **Endpoint**: POST `/api/mapping/jobs`
- **Target**: 20 requests/second
- **Success Criteria**:
  - [ ] 95th percentile response time < 2s
  - [ ] Error rate < 2%

#### 5.4 Export Download Load Test
- **Endpoint**: GET `/api/export/{job_id}/xlsx`
- **Target**: 10 requests/second
- **Success Criteria**:
  - [ ] 95th percentile response time < 3s
  - [ ] Error rate < 1%

### Load Test Results Template
```
| Metric                  | Login | Products | Mapping | Export |
|------------------------|-------|----------|---------|--------|
| Avg Response Time (ms) |       |          |         |        |
| 95th Percentile (ms)   |       |          |         |        |
| Max Response Time (ms) |       |          |         |        |
| Requests/sec           |       |          |         |        |
| Error Rate (%)         |       |          |         |        |
| Status                 |       |          |         |        |
```

---

## 6. Phase 1 Acceptance Criteria Verification

### AC-1: Shopify Connection
- [ ] Can connect a Shopify store using domain and access token
- [ ] Connection is persisted and token is encrypted
- [ ] Can sync at least 10 products from connected store

### AC-2: Template Schemas
- [ ] Two template schemas ingested: `amazon_shirt_v1` and `amazon_kurta_v1`
- [ ] Schemas stored in MongoDB `template_schemas` collection
- [ ] Schemas have correct column definitions with col_index

### AC-3: Auto-Fill Rate
- [ ] For 80% of test products, at least 70% of canonical fields are auto-filled
- [ ] Auto-fill includes both rule-based and AI-assisted mappings
- [ ] Confidence scores are accurate

**Test Data:**
| Product | Total Fields | Auto-Filled | Rate | Passing |
|---------|--------------|-------------|------|---------|
| Shirt 1 | 10           |             |      |         |
| Shirt 2 | 10           |             |      |         |
| Kurta 1 | 10           |             |      |         |
| Kurta 2 | 10           |             |      |         |
| ...     | ...          |             |      |         |

### AC-4: Mapping Preview UI
- [ ] Confidence badges displayed with correct colors
- [ ] Inline editing works for all field types
- [ ] "Approve All Suggested" button updates AI suggestions
- [ ] User can override any field value

### AC-5: Export Functionality
- [ ] Downloaded XLSX opens in Excel without errors
- [ ] Columns are in correct order (by col_index)
- [ ] Required fields are highlighted in header
- [ ] Parent-child variations render as multiple rows (if applicable)

### AC-6: Logging and Validation
- [ ] Validation report available for each mapping job
- [ ] Errors clearly identify field and issue
- [ ] Job status reflects validation state

---

## 7. Bug Tracking Template

| ID | Severity | Component | Description | Steps to Reproduce | Expected | Actual | Status |
|----|----------|-----------|-------------|--------------------|----------|--------|--------|
|    |          |           |             |                    |          |        |        |

**Severity Levels:**
- **P0**: Critical - Blocks all testing
- **P1**: High - Major feature broken
- **P2**: Medium - Feature works with workaround
- **P3**: Low - Minor issue, cosmetic

---

## 8. Sign-Off

### Tester Sign-Off
- **Tester Name**: _________________
- **Date**: _________________
- **Overall Status**: [ ] Pass [ ] Fail
- **Notes**:

### Developer Sign-Off
- **Developer Name**: _________________
- **Date**: _________________
- **All Critical Bugs Fixed**: [ ] Yes [ ] No
- **Notes**:

---

## Appendix: Test Data

### Sample Product JSON
```json
{
  "id": "prod_test_001",
  "title": "Premium Cotton T-Shirt - Blue",
  "description": "100% organic cotton t-shirt. Soft, breathable fabric.",
  "vendor": "Test Brand",
  "product_type": "Shirt",
  "tags": ["cotton", "summer", "casual"],
  "variants": [
    {
      "id": "var_001",
      "sku": "TEST-BLU-S",
      "price": "29.99",
      "option1": "Small",
      "option2": "Blue"
    }
  ]
}
```

### Sample Schema (amazon_shirt_v1)
```json
{
  "schema_id": "amazon_shirt_v1",
  "marketplace": "amazon",
  "category": "shirt",
  "columns": [
    {"col_index": 0, "canonical": "sku", "required": true},
    {"col_index": 1, "canonical": "title", "required": true},
    {"col_index": 2, "canonical": "brand", "required": true},
    {"col_index": 3, "canonical": "price", "required": true, "type": "float"},
    {"col_index": 4, "canonical": "color", "required": true},
    {"col_index": 5, "canonical": "size", "required": true, "enum": ["S","M","L","XL"]},
    {"col_index": 6, "canonical": "fabric", "required": false, "enum": ["Cotton","Polyester"]}
  ]
}
```

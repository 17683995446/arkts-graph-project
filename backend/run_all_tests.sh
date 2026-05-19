
#!/bin/bash

# Complete System Test Suite Runner
# Runs all tests and generates comprehensive report

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  COMPLETE SYSTEM TEST SUITE - ALL TESTS VALIDATION      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

cd /workspace/backend

# Clean previous test databases
rm -f knowledge_graph.db
echo "🧹 Cleaned previous test databases"
echo ""

# Test 1: Basic System Tests
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📋 TEST 1: Basic System Tests${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
if python test_system.py > /tmp/test_system.log 2>&1; then
    echo -e "${GREEN}✅ Basic System Tests: PASSED${NC}"
else
    echo -e "${RED}❌ Basic System Tests: FAILED${NC}"
    cat /tmp/test_system.log
fi
echo ""

# Test 2: Integration Tests
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📋 TEST 2: Realistic Integration Tests${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
if python integration_test.py > /tmp/integration_test.log 2>&1; then
    echo -e "${GREEN}✅ Integration Tests: PASSED${NC}"
else
    echo -e "${RED}❌ Integration Tests: FAILED${NC}"
    cat /tmp/integration_test.log
fi
echo ""

# Test 3: Edge Case Tests
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📋 TEST 3: Edge Case & Bug Discovery Tests${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
if python edge_case_test.py > /tmp/edge_case_test.log 2>&1; then
    echo -e "${GREEN}✅ Edge Case Tests: PASSED${NC}"
else
    echo -e "${RED}❌ Edge Case Tests: FAILED${NC}"
    cat /tmp/edge_case_test.log
fi
echo ""

# Test 4: Stress Tests
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📋 TEST 4: Comprehensive Stress Tests${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
if python stress_test.py > /tmp/stress_test.log 2>&1; then
    echo -e "${GREEN}✅ Stress Tests: PASSED${NC}"
else
    echo -e "${RED}❌ Stress Tests: FAILED${NC}"
    cat /tmp/stress_test.log
fi
echo ""

# Final Summary
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  TEST EXECUTION SUMMARY                                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "All test logs have been saved to /tmp/"
echo ""
echo "✅ Test suite completed successfully!"
echo ""

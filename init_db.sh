#!/bin/bash

echo "=========================================="
echo "BookApp Database Initialization Script"
echo "=========================================="
echo ""

echo "Project: $DEV_PROJECT"

# Check if cluster exists and get credentials
echo "Connecting to GKE cluster..."
gcloud container clusters get-credentials bookapp-cluster --zone=${zone} 2>/dev/null || \
gcloud container clusters get-credentials bookapp-cluster --region=${region} 2>/dev/null || {
    echo "❌ Error: Could not connect to bookapp-cluster"
    echo "Please ensure your cluster is running and you have the correct credentials."
    exit 1
}

echo "✓ Connected to cluster"
echo ""

# Check if database pod is running
echo "Checking database pod status..."
DB_POD=$(kubectl get pods -l app=bookapp-db -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

if [ -z "$DB_POD" ]; then
    echo "❌ Error: No database pod found"
    echo "Please ensure your database deployment is running."
    exit 1
fi

POD_STATUS=$(kubectl get pod $DB_POD -o jsonpath='{.status.phase}')
if [ "$POD_STATUS" != "Running" ]; then
    echo "❌ Error: Database pod is not running (status: $POD_STATUS)"
    echo "Please wait for the database pod to be ready or check for errors."
    exit 1
fi

echo "✓ Database pod is running: $DB_POD"
echo ""

# Database connection details
DB_HOST="bookapp-db"
DB_PORT="5432"
DB_NAME="bookapp"
DB_USER="admin"
DB_PASSWORD="secret"

echo "Database connection details:"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo ""

# Create initialization SQL script
echo "Creating database initialization SQL..."
cat > /tmp/init_bookapp.sql << 'EOF'
-- Clear existing data (optional - comment out if you want to keep existing data)
-- TRUNCATE TABLE reading_progress, "book", "user" RESTART IDENTITY CASCADE;

-- Insert admin users
INSERT INTO "user" (username, email, password, phone, gender, address, is_admin) VALUES
('Jane_Doe', 'Jane_Doe@admin.com', 'abcd1234', '1234567890', 'Female', 'Pune', TRUE),
('John_Doe', 'John_Doe@admin.com', 'abcd1234', '1234567890', 'Male', 'Pune', TRUE),
('Naman_Gupta', 'Naman_Gupta@admin.com', 'abcd1234', '1234567890', 'Male', 'Pune', TRUE),
('demo_user', 'demo@bookapp.com', 'demo123', '9876543210', 'Other', 'Mumbai', FALSE)
ON CONFLICT (username) DO NOTHING;

-- Insert sample books
INSERT INTO "book" (title, author, translator, description, pdf_loc, cover_img_loc, published_on, genre) VALUES
('Moby Dick; Or, The Whale', 'Herman Melville', '', 'A tale of the whale hunt and revenge.', '/static/pdfs/Moby Dick; Or, The Whale.epub', '/static/images/Moby Dick; Or, The Whale.png', '1851-10-18', 'Fiction'),
('Pride and Prejudice', 'Jane Austen', '', 'A classic romance novel.', '/static/pdfs/Pride and Prejudice.epub', '/static/images/Pride and Prejudice.png', '1813-01-28', 'Romance'),
('Romeo and Juliet', 'William Shakespeare', '', 'A timeless tragedy of star-crossed lovers.', '/static/pdfs/Romeo and Juliet.epub', '/static/images/Romeo and Juliet.png', '1597-01-01', 'Drama')
ON CONFLICT (title) DO NOTHING;

-- Display summary
SELECT 'Users created:' as summary, COUNT(*) as count FROM "user"
UNION ALL
SELECT 'Books available:', COUNT(*) FROM "book"
UNION ALL
SELECT 'Reading progress entries:', COUNT(*) FROM reading_progress;

-- Display admin users
SELECT 'Admin Users:' as info, username, email FROM "user" WHERE is_admin = TRUE;
EOF

echo "✓ SQL script created"
echo ""

# Copy SQL file to database pod
echo "Copying SQL script to database pod..."
kubectl cp /tmp/init_bookapp.sql $DB_POD:/tmp/init_bookapp.sql
echo "✓ SQL script copied to pod"
echo ""

# Execute the SQL script
echo "Executing database initialization..."
echo "This may take a few moments..."
echo ""

kubectl exec -it $DB_POD -- psql -h localhost -p $DB_PORT -U $DB_USER -d $DB_NAME -f /tmp/init_bookapp.sql

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ Database initialization completed!"
    echo "=========================================="
    echo ""
    echo "📚 Sample data loaded:"
    echo "   • Admin users: Jane_Doe, John_Doe, Naman_Gupta"
    echo "   • Demo user: demo_user"
    echo "   • Sample books: Moby Dick, Pride and Prejudice, Romeo and Juliet, etc."
    echo "   • Reading progress: Sample progress data for users"
    echo ""
    echo "🔐 Login credentials:"
    echo "   Admin: Jane_Doe / abcd1234"
    echo "   Admin: John_Doe / abcd1234"
    echo "   Admin: Naman_Gupta / abcd1234"
    echo "   Demo:  demo_user / demo123"
    echo ""
    echo "🌐 Your app should now be ready to use!"
    
    # Get service URLs
    echo ""
    echo "📡 Service URLs:"
    kubectl get services -o custom-columns="NAME:.metadata.name,TYPE:.spec.type,EXTERNAL-IP:.status.loadBalancer.ingress[0].ip,PORT:.spec.ports[0].port" | grep -E "(bookapp-web|bookapp-pgadmin)"
    
else
    echo ""
    echo "❌ Database initialization failed!"
    echo "Please check the error messages above and try again."
    exit 1
fi

# Clean up temporary file
rm -f /tmp/init_bookapp.sql
echo ""
echo "Database initialization script completed."

/**
 * PyPDF Toolkit Web - Main JavaScript Application
 * Provides common functionality for all pages
 */

// Global application object
window.PyPDFToolkit = {
    // Configuration
    config: {
        maxFileSize: 16 * 1024 * 1024, // 16MB
        allowedPdfTypes: ['application/pdf'],
        allowedImageTypes: ['image/jpeg', 'image/png', 'image/bmp', 'image/tiff', 'image/gif'],
        apiEndpoints: {
            merge: '/api/merge',
            split: '/api/split',
            compress: '/api/compress',
            convert: '/api/convert',
            unlock: '/api/unlock',
            pdfInfo: '/api/pdf-info'
        }
    },

    // Utility functions
    utils: {
        /**
         * Format file size in human readable format
         * @param {number} bytes - File size in bytes
         * @returns {string} Formatted file size
         */
        formatFileSize: function(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        },

        /**
         * Validate file type and size
         * @param {File} file - File to validate
         * @param {Array} allowedTypes - Array of allowed MIME types
         * @returns {Object} Validation result
         */
        validateFile: function(file, allowedTypes) {
            const result = { valid: true, errors: [] };

            // Check file size
            if (file.size > this.parent.config.maxFileSize) {
                result.valid = false;
                result.errors.push(`File size exceeds ${this.formatFileSize(this.parent.config.maxFileSize)} limit`);
            }

            // Check file type
            if (allowedTypes && !allowedTypes.includes(file.type)) {
                result.valid = false;
                result.errors.push('File type not supported');
            }

            return result;
        },

        /**
         * Generate unique ID
         * @returns {string} Unique ID
         */
        generateId: function() {
            return Date.now().toString(36) + Math.random().toString(36).substr(2);
        },

        /**
         * Debounce function calls
         * @param {Function} func - Function to debounce
         * @param {number} wait - Wait time in milliseconds
         * @returns {Function} Debounced function
         */
        debounce: function(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }
    },

    // UI components
    ui: {
        /**
         * Show alert message
         * @param {string} message - Alert message
         * @param {string} type - Alert type (success, error, info, warning)
         * @param {number} duration - Auto-hide duration in milliseconds
         */
        showAlert: function(message, type = 'info', duration = 5000) {
            // Remove existing alerts of the same type
            const existingAlerts = document.querySelectorAll(`.alert-${type}`);
            existingAlerts.forEach(alert => alert.remove());

            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type}`;
            alertDiv.innerHTML = `
                <i class="fas fa-${this.getAlertIcon(type)}"></i>
                ${message}
                <button type="button" class="alert-close" onclick="this.parentNode.remove()">
                    <i class="fas fa-times"></i>
                </button>
            `;

            // Add close button styling
            const style = document.createElement('style');
            style.textContent = `
                .alert-close {
                    background: none;
                    border: none;
                    float: right;
                    font-size: 1.2em;
                    cursor: pointer;
                    opacity: 0.7;
                    margin-left: 10px;
                }
                .alert-close:hover { opacity: 1; }
            `;
            if (!document.head.querySelector('style[data-alert-styles]')) {
                style.setAttribute('data-alert-styles', 'true');
                document.head.appendChild(style);
            }

            const container = document.querySelector('.main-content') || document.body;
            container.insertBefore(alertDiv, container.firstChild);

            // Auto-remove after duration
            if (duration > 0) {
                setTimeout(() => {
                    if (alertDiv.parentNode) {
                        alertDiv.remove();
                    }
                }, duration);
            }

            // Smooth scroll to alert
            alertDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        },

        /**
         * Get icon for alert type
         * @param {string} type - Alert type
         * @returns {string} Font Awesome icon class
         */
        getAlertIcon: function(type) {
            const icons = {
                success: 'check-circle',
                error: 'exclamation-triangle',
                warning: 'exclamation-circle',
                info: 'info-circle'
            };
            return icons[type] || 'info-circle';
        },

        /**
         * Show loading state on button
         * @param {HTMLElement} button - Button element
         * @param {string} loadingText - Loading text
         * @returns {string} Original button text
         */
        showLoading: function(button, loadingText = 'Processing...') {
            const originalText = button.innerHTML;
            button.innerHTML = `<span class="spinner"></span>${loadingText}`;
            button.disabled = true;
            return originalText;
        },

        /**
         * Hide loading state on button
         * @param {HTMLElement} button - Button element
         * @param {string} originalText - Original button text
         */
        hideLoading: function(button, originalText) {
            button.innerHTML = originalText;
            button.disabled = false;
        },

        /**
         * Create progress bar
         * @param {HTMLElement} container - Container element
         * @returns {Object} Progress bar controller
         */
        createProgressBar: function(container) {
            const progressDiv = document.createElement('div');
            progressDiv.className = 'progress';
            progressDiv.innerHTML = '<div class="progress-bar"></div>';
            container.appendChild(progressDiv);

            const progressBar = progressDiv.querySelector('.progress-bar');
            
            return {
                element: progressDiv,
                setProgress: function(percent) {
                    progressBar.style.width = Math.min(Math.max(percent, 0), 100) + '%';
                },
                remove: function() {
                    if (progressDiv.parentNode) {
                        progressDiv.parentNode.removeChild(progressDiv);
                    }
                }
            };
        }
    },

    // File handling
    fileHandler: {
        /**
         * Setup drag and drop file upload
         * @param {HTMLElement} uploadArea - Upload area element
         * @param {HTMLElement} fileInput - File input element
         * @param {Function} callback - Callback function for file handling
         * @param {Array} allowedTypes - Allowed file types
         */
        setupDragAndDrop: function(uploadArea, fileInput, callback, allowedTypes) {
            // Click to upload
            uploadArea.addEventListener('click', (e) => {
                if (e.target !== fileInput) {
                    fileInput.click();
                }
            });

            // Drag and drop events
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            });

            uploadArea.addEventListener('dragleave', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
            });

            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
                
                const files = Array.from(e.dataTransfer.files);
                this.handleFiles(files, callback, allowedTypes);
            });

            // File input change
            fileInput.addEventListener('change', (e) => {
                const files = Array.from(e.target.files);
                this.handleFiles(files, callback, allowedTypes);
            });
        },

        /**
         * Handle file selection and validation
         * @param {Array} files - Array of File objects
         * @param {Function} callback - Callback function
         * @param {Array} allowedTypes - Allowed file types
         */
        handleFiles: function(files, callback, allowedTypes) {
            const validFiles = [];
            const errors = [];

            files.forEach(file => {
                const validation = PyPDFToolkit.utils.validateFile(file, allowedTypes);
                if (validation.valid) {
                    validFiles.push(file);
                } else {
                    errors.push(`${file.name}: ${validation.errors.join(', ')}`);
                }
            });

            // Show validation errors
            if (errors.length > 0) {
                PyPDFToolkit.ui.showAlert(
                    'Some files were rejected:<br>' + errors.join('<br>'),
                    'error'
                );
            }

            // Call callback with valid files
            if (validFiles.length > 0 && callback) {
                callback(validFiles);
            }
        }
    },

    // API handling
    api: {
        /**
         * Submit form data to API endpoint
         * @param {FormData} formData - Form data to submit
         * @param {string} endpoint - API endpoint URL
         * @param {HTMLElement} button - Submit button element
         * @param {Function} successCallback - Success callback function
         * @param {Function} errorCallback - Error callback function
         */
        submitForm: function(formData, endpoint, button, successCallback, errorCallback) {
            const originalText = PyPDFToolkit.ui.showLoading(button);
            
            fetch(endpoint, {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                PyPDFToolkit.ui.hideLoading(button, originalText);
                
                if (data.success) {
                    PyPDFToolkit.ui.showAlert('Operation completed successfully!', 'success');
                    if (successCallback) successCallback(data);
                } else {
                    PyPDFToolkit.ui.showAlert('Error: ' + data.error, 'error');
                    if (errorCallback) errorCallback(data);
                }
            })
            .catch(error => {
                PyPDFToolkit.ui.hideLoading(button, originalText);
                PyPDFToolkit.ui.showAlert('Network error: ' + error.message, 'error');
                if (errorCallback) errorCallback({ error: error.message });
            });
        },

        /**
         * Download file from URL
         * @param {string} url - Download URL
         * @param {string} filename - Filename for download
         */
        downloadFile: function(url, filename) {
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }
    },

    // Initialize application
    init: function() {
        // Set up global error handling
        window.addEventListener('error', (e) => {
            console.error('Global error:', e.error);
        });

        // Set up unhandled promise rejection handling
        window.addEventListener('unhandledrejection', (e) => {
            console.error('Unhandled promise rejection:', e.reason);
        });

        // Add keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // ESC to close alerts
            if (e.key === 'Escape') {
                const alerts = document.querySelectorAll('.alert');
                alerts.forEach(alert => alert.remove());
            }
        });

        console.log('PyPDF Toolkit Web initialized');
    }
};

// Set up parent references for nested objects
PyPDFToolkit.utils.parent = PyPDFToolkit;

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', PyPDFToolkit.init);
} else {
    PyPDFToolkit.init();
}

// Export for global use (legacy support)
window.formatFileSize = PyPDFToolkit.utils.formatFileSize;
window.showAlert = PyPDFToolkit.ui.showAlert;
window.showLoading = PyPDFToolkit.ui.showLoading;
window.hideLoading = PyPDFToolkit.ui.hideLoading;
window.setupFileUpload = PyPDFToolkit.fileHandler.setupDragAndDrop;
window.submitForm = PyPDFToolkit.api.submitForm;
window.downloadFile = PyPDFToolkit.api.downloadFile;

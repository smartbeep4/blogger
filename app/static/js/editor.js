// Editor-specific JavaScript functionality
// This file contains additional editor features beyond the Alpine.js inline code

document.addEventListener('DOMContentLoaded', function() {
    // Additional Quill.js customization
    const quill = document.querySelector('#editor');
    if (quill) {
        // Add keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            // Ctrl/Cmd + S to save draft
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                const saveBtn = document.querySelector('button[onclick*="saveDraft"]');
                if (saveBtn) {
                    saveBtn.click();
                }
            }

            // Ctrl/Cmd + P to preview
            if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
                e.preventDefault();
                const previewBtn = document.querySelector('button[onclick*="preview"]');
                if (previewBtn) {
                    previewBtn.click();
                }
            }
        });

        // Auto-focus on title if empty
        const titleInput = document.getElementById('title');
        if (titleInput && !titleInput.value) {
            titleInput.focus();
        }
    }

    // File upload progress indicators
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Show file size warning for large files
                const sizeMB = file.size / (1024 * 1024);
                if (sizeMB > 10) {
                    alert(`Warning: File size is ${sizeMB.toFixed(1)}MB. Large files may take time to upload.`);
                }
            }
        });
    });

    // Confirm before leaving page with unsaved changes
    let hasUnsavedChanges = false;
    const originalTitle = document.getElementById('title')?.value || '';
    const originalContent = document.querySelector('.ql-editor')?.innerHTML || '';

    function checkForChanges() {
        const currentTitle = document.getElementById('title')?.value || '';
        const currentContent = document.querySelector('.ql-editor')?.innerHTML || '';

        hasUnsavedChanges = currentTitle !== originalTitle || currentContent !== originalContent;
    }

    // Check for changes periodically
    setInterval(checkForChanges, 5000);

    // Warn before leaving
    window.addEventListener('beforeunload', function(e) {
        if (hasUnsavedChanges) {
            e.preventDefault();
            e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
            return e.returnValue;
        }
    });

    // Enhanced form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const titleInput = document.getElementById('title');
            if (titleInput && !titleInput.value.trim()) {
                e.preventDefault();
                alert('Please enter a title for your post.');
                titleInput.focus();
                return;
            }

            const editor = document.querySelector('.ql-editor');
            if (editor && !editor.textContent.trim()) {
                e.preventDefault();
                alert('Please add some content to your post.');
                editor.focus();
                return;
            }
        });
    });

    // Initialize tooltips for toolbar buttons
    const toolbarButtons = document.querySelectorAll('#toolbar button');
    toolbarButtons.forEach(button => {
        if (button.title) {
            button.setAttribute('data-tooltip', button.title);
        }
    });

    // Auto-resize textareas in modals
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });
});

// Utility functions for the editor
function formatJsonForDisplay(jsonString) {
    try {
        const obj = JSON.parse(jsonString);
        return JSON.stringify(obj, null, 2);
    } catch (e) {
        return jsonString;
    }
}

function validateChartData(data) {
    try {
        const parsed = JSON.parse(data);
        if (!parsed.labels || !Array.isArray(parsed.labels)) {
            throw new Error('Chart data must have a "labels" array');
        }
        if (!parsed.datasets || !Array.isArray(parsed.datasets)) {
            throw new Error('Chart data must have a "datasets" array');
        }
        return true;
    } catch (e) {
        alert('Invalid chart data: ' + e.message);
        return false;
    }
}

function validateQuizData(type, question, answer, options) {
    if (!question.trim()) {
        alert('Please enter a question.');
        return false;
    }

    if (!answer.trim()) {
        alert('Please enter the correct answer.');
        return false;
    }

    if (type === 'multiple_choice') {
        const optionsArray = options.split('\n').filter(opt => opt.trim());
        if (optionsArray.length < 2) {
            alert('Multiple choice questions need at least 2 options.');
            return false;
        }

        if (!optionsArray.includes(answer.trim())) {
            alert('The correct answer must be one of the options.');
            return false;
        }
    }

    return true;
}

// Export functions for use in other scripts
window.EditorUtils = {
    formatJsonForDisplay,
    validateChartData,
    validateQuizData
};

/**
 * Format a date string safely without timezone shifting
 * @param {string} dateString - The date string to format
 * @returns {string} - Formatted date string
 */
function formatDateSafe(dateString) {
    if (!dateString) return '';

    try {
        // Extract date components directly from YYYY-MM-DD format
        const match = dateString.match(/^(\d{4})-(\d{2})-(\d{2})/);
        if (match) {
            const year = parseInt(match[1], 10);
            const month = parseInt(match[2], 10) - 1; // JS months are 0-indexed
            const day = parseInt(match[3], 10);

            // Create date without timezone shifting
            const date = new Date(year, month, day);

            // Verify date is valid
            if (isNaN(date.getTime())) {
                return dateString; // Return original if parsing failed
            }

            // Format using locale-specific date format
            return date.toLocaleDateString();
        }

        // Fallback to original format function if not in expected format
        return formatDate(dateString);
    } catch (error) {
        console.error('Error safely formatting date:', error);
        return dateString;
    }
}

/**
 * Format a datetime string safely without timezone shifting
 * @param {string} dateTimeString - The datetime string to format (e.g., "2025-04-01 14:30:00")
 * @param {boolean} includeTime - Whether to include time in the formatted output (default: true)
 * @returns {string} - Formatted datetime string
 */
function formatDateTime(dateTimeString, includeTime = true) {
    if (!dateTimeString) return '';

    try {
        // Extract date and time components directly from string
        // Match format like "2025-04-01 14:30:00" or "2025-04-01T14:30:00"
        const match = dateTimeString.match(/^(\d{4})-(\d{2})-(\d{2})[T\s](\d{2}):(\d{2}):(\d{2})/);

        if (match) {
            const year = parseInt(match[1], 10);
            const month = parseInt(match[2], 10) - 1; // JS months are 0-indexed
            const day = parseInt(match[3], 10);
            const hours = parseInt(match[4], 10);
            const minutes = parseInt(match[5], 10);
            const seconds = parseInt(match[6], 10);

            // Create date without timezone shifting by specifying all components
            const date = new Date(year, month, day, hours, minutes, seconds);

            // Verify date is valid
            if (isNaN(date.getTime())) {
                console.warn('Invalid date created from:', dateTimeString);
                return dateTimeString; // Return original if parsing failed
            }

            // Format options
            const options = {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            };

            // Add time options if requested
            if (includeTime) {
                options.hour = '2-digit';
                options.minute = '2-digit';
                options.hour12 = true; // Use 12-hour format (AM/PM)
            }

            // Format using locale-specific datetime format
            return date.toLocaleString(undefined, options);
        }

        // Check for date-only format (YYYY-MM-DD)
        const dateOnlyMatch = dateTimeString.match(/^(\d{4})-(\d{2})-(\d{2})$/);
        if (dateOnlyMatch) {
            const year = parseInt(dateOnlyMatch[1], 10);
            const month = parseInt(dateOnlyMatch[2], 10) - 1;
            const day = parseInt(dateOnlyMatch[3], 10);

            const date = new Date(year, month, day);

            if (isNaN(date.getTime())) {
                return dateTimeString;
            }

            return date.toLocaleDateString();
        }

        // If no pattern matches, try direct parsing as fallback
        // (but this may cause timezone shifts)
        const directDate = new Date(dateTimeString);
        if (!isNaN(directDate.getTime())) {
            console.warn('Using direct date parsing which may cause timezone shifts:', dateTimeString);

            const options = {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            };

            if (includeTime) {
                options.hour = '2-digit';
                options.minute = '2-digit';
                options.hour12 = true;
            }

            return directDate.toLocaleString(undefined, options);
        }

        // Return original string if all parsing attempts fail
        return dateTimeString;
    } catch (error) {
        console.error('Error formatting datetime:', error);
        return dateTimeString;
    }
}
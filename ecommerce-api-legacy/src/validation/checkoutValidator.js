function normalizeCheckoutPayload(body) {
    return {
        userName: body.userName || body.usr,
        email: body.email || body.eml,
        password: body.password || body.pwd,
        courseId: body.courseId || body.c_id,
        cardNumber: body.cardNumber || body.card,
    };
}

function validateCheckoutPayload(payload) {
    const details = [];

    if (!payload.userName) {
        details.push('userName is required');
    }

    if (!payload.email) {
        details.push('email is required');
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(payload.email)) {
        details.push('email must be valid');
    }

    if (!payload.password) {
        details.push('password is required');
    }

    if (!Number.isInteger(Number(payload.courseId)) || Number(payload.courseId) <= 0) {
        details.push('courseId must be a positive integer');
    }

    if (!payload.cardNumber) {
        details.push('cardNumber is required');
    } else if (!/^\d{13,19}$/.test(String(payload.cardNumber))) {
        details.push('cardNumber must contain 13 to 19 digits');
    }

    return details;
}

module.exports = { normalizeCheckoutPayload, validateCheckoutPayload };

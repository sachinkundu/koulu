import { MAILHOG_URL } from './env';

interface MailHogMessage {
  ID: string;
  Content: {
    Headers: Record<string, string[]>;
    Body: string;
  };
  MIME?: {
    Parts: Array<{
      Headers: Record<string, string[]>;
      Body: string;
    }>;
  };
}

interface MailHogSearchResponse {
  total: number;
  count: number;
  start: number;
  items: MailHogMessage[];
}

function getEmailBody(message: MailHogMessage): string {
  // Try MIME parts first (multipart emails have decoded/parseable parts)
  if (message.MIME?.Parts) {
    for (const part of message.MIME.Parts) {
      if (part.Body) {
        const transferEncoding = part.Headers?.['Content-Transfer-Encoding']?.[0];
        if (transferEncoding === 'base64') {
          return Buffer.from(part.Body, 'base64').toString('utf-8');
        }
        return part.Body;
      }
    }
  }

  // Fall back to direct body (simple non-multipart emails)
  if (message.Content.Body) {
    return message.Content.Body;
  }

  return '';
}

/**
 * Fetch the verification token from a verification email sent to the given address.
 * Retries up to maxRetries times with 1s delay between attempts.
 */
export async function getVerificationToken(
  email: string,
  maxRetries = 10,
): Promise<string> {
  for (let i = 0; i < maxRetries; i++) {
    const response = await fetch(
      `${MAILHOG_URL}/api/v2/search?kind=to&query=${encodeURIComponent(email)}`,
    );
    const data: MailHogSearchResponse = await response.json();

    if (data.items.length > 0) {
      // Use the latest email
      const message = data.items[data.items.length - 1];
      const body = getEmailBody(message);

      // Extract token from verification link: /verify?token=<token>
      const match = body.match(/verify\?token=([^"&\s<]+)/);
      if (match) {
        return decodeURIComponent(match[1]);
      }
    }

    // Wait before retrying
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }

  throw new Error(
    `No verification email found for ${email} after ${maxRetries} retries`,
  );
}

/**
 * Delete all emails in MailHog. Useful for test cleanup.
 */
export async function clearEmails(): Promise<void> {
  await fetch(`${MAILHOG_URL}/api/v1/messages`, { method: 'DELETE' });
}

/** LMS Question.data may arrive as a parsed object (authoring) or a JSON
 *  string (from frappe.get_all in the player fetch). Normalize to an object. */
export function parseConfig(question: any): Record<string, any> {
	const raw = question?.data
	if (!raw) return {}
	if (typeof raw === 'string') {
		try {
			return JSON.parse(raw) || {}
		} catch {
			return {}
		}
	}
	return raw
}

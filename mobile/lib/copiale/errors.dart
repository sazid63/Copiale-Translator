/// Shared error type for the Copiale translator port.
library;

/// Raised for anything the translator cannot represent. Nothing is ever
/// dropped or substituted silently.
class CopialeError implements Exception {
  final String message;
  CopialeError(this.message);
  @override
  String toString() => 'CopialeError: $message';
}

#: Error raised when a file with the wrong format is loaded by the user.
class UnsupportedFileFormatError(Exception): pass

#: Error raised when no hike ID in the database is associated to a magic link.
class NoHikeForMagicLink(Exception): pass

#: Error raised when there is no hike data associated to to the user
class NoHikeForUser(Exception): pass

#: Error raised when no hike ID in the database is found.
class NoHikeIDInDB(Exception): pass

#/ Error raised when there is no hike with the given name in the database
class NoHikeNameInDb(Exception): pass

#: Error raised when no magic link ID in the database is found.
class NoMagicLinkIDInDB(Exception): pass

#: Error raised when no magic link is associated to a given hike ID.
class NoMagicLinkForHikeID(Exception): pass

#: Error raised when there is no 
class NoUsernameInDB(Exception): pass

#: Error raised when the user ID does not exist in the database
class NoUserIdInDB(Exception): pass

#: Error raised when the username for login is wrong
class WrongUsername(Exception): pass

#: Error raised when the password for login is wrong
class WrongPassword(Exception): pass

#: Error raised when an error occurs during the processing of GeoJson data
class GeoJsonParsingFailed(Exception): pass
[](Free%20actions%20are%20caused%20by%20prior%20events%20involving%20the%20agent,%20but%20this%20causation%20is%20indeterministic.md)[](Free%20actions%20are%20caused%20by%20prior%20events%20involving%20the%20agent,%20but%20this%20causation%20is%20indeterministic.md)[](Free%20actions%20are%20caused%20by%20prior%20events%20involving%20the%20agent,%20but%20this%20causation%20is%20indeterministic.md)[](Free%20actions%20are%20caused%20by%20prior%20events%20involving%20the%20agent,%20but%20this%20causation%20is%20indeterministic.md)[](Free%20actions%20are%20not%20the%20result%20of%20causation.md)[](Free%20actions%20are%20not%20the%20result%20of%20causation.md)[](Free%20actions%20are%20not%20the%20result%20of%20causation.md)[](Free%20actions%20are%20not%20the%20result%20of%20causation.md)[](Free%20actions%20originate%20in%20the%20agent,%20a%20persisting%20entity%20and%20not%20an%20event.md)[](Free%20actions%20originate%20in%20the%20agent,%20a%20persisting%20entity%20and%20not%20an%20event.md)#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#Adapted from https://notabug.org/uhuxybim/DeDRM_tools-LCP
#Adaption by meaclam, 2022

# lcpdedrm.py
# Copyright © 2021 NoDRM

# Released under the terms of the GNU General Public Licence, version 3
# <http://www.gnu.org/licenses/>

"""
Decrypt Readium LCP encrypted audiobooks.
"""

__license__ = 'GPL v3'
__version__ = "1"

from genericpath import exists
from itertools import count
import json
import hashlib
import base64
import binascii
import os.path
import shutil
from zipfile import ZipFile
import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
import pip
pip.main(['install','pycryptodome'])
from Crypto.Cipher import AES


class Run:
    def __init__(self):
        root = tk.Tk()
        root.withdraw()

        #Select a zip file with .mp3 audio files, license.lcpl and manifest.json
        file_path = filedialog.askopenfilename()
        self.path_to_ebook = file_path

        if exists("passphrase.txt"):
            f = open("passphrase.txt", "r")
            self.passphrase = [f.read()]
            f.close()
        else:
            self.passphrase = -1 
        #self.passphrase = ["01485216"]   # <- uncomment and edit here

    def start(self):
        if(self.passphrase != -1):
            self.passphrase = [simpledialog.askstring("Passphrase", "What is your passphrase?", initialvalue=self.passphrase[0])]
        else:
            self.passphrase = [simpledialog.askstring("Passphrase", "What is your passphrase?")]

        f = open("passphrase.txt", "w")
        f.write(self.passphrase[0])
        f.close()

        decryptLCPbook(self.path_to_ebook, self.passphrase, self)


class Decryptor(object):
    def __init__(self, bookkey):
        self.book_key = bookkey

    def decrypt(self, data):
        aes = AES.new(self.book_key, AES.MODE_CBC, data[:16])
        data = aes.decrypt(data[16:])

        return data


class LCPError(Exception):
    pass


class LCPTransform:

    @staticmethod
    def secret_transform_basic(input_hash):
        # basic profile doesn't have any transformation
        # Takes key input as hexdigest and outputs it as hexdigest
        return input_hash

    @staticmethod
    def secret_transform_profile10(input_hash):
        # Takes an input sha256 hash as hexdigest and transforms that according to the profile-1.0 spec. 
        # This 64-byte master key is basically all that distinguishes the open source "open for everyone" version
        # from the so-called "open source" closed-source-version that's actually being used by book distributors.
        # 64 byte master key = 64 iterations

        # This function is what the documentation describes as "uk = userkey(h)", the "secret userkey transform"

        # 1. Take input
        # 2. Hash it
        # 3. Add one byte from the master key to the end of the hash
        # 4. Hash that result again
        # 5. Go back to 3. until you run out of bytes. 
        # 6. The result is the key.

        masterkey = "b3a07c4d42880e69398e05392405050efeea0664c0b638b7c986556fa9b58d77b31a40eb6a4fdba1e4537229d9f779daad1cc41ee968153cb71f27dc9696d40f"
        masterkey = bytearray.fromhex(masterkey)

        current_hash = bytearray.fromhex(input_hash)

        for byte in masterkey:
            current_hash.append(byte)
            current_hash = bytearray(hashlib.sha256(current_hash).digest())
        return binascii.hexlify(current_hash).decode("latin-1")

    @staticmethod
    def userpass_to_hash(passphrase, algorithm):
        # Check for the password algorithm. The Readium LCP standard only defines SHA256.
        # The hashing standard documents they link to define a couple other hash algorithms, too. 
        # I've never seen them actually used in an LCP-encrypted file, so I didn't bother to implement them. 

        if (algorithm == "http://www.w3.org/2001/04/xmlenc#sha256"):
            algo = "SHA256"
            user_password_hashed = hashlib.sha256(passphrase).hexdigest()
            # This seems to be the only algorithm that's actually defined in the Readium standard.
        else:
            print("LCP: Book is using unsupported user key algorithm: {0}".format(algorithm))
            return None, None

        return algo, user_password_hashed


# This function decrypts data with the given key
def dataDecryptLCP(b64data, hex_key):
    try:
        iv = base64.decodebytes(b64data.encode('ascii'))[:16]
        cipher = base64.decodebytes(b64data.encode('ascii'))[16:]
    except AttributeError:
        iv = base64.decodestring(b64data.encode('ascii'))[:16]
        cipher = base64.decodestring(b64data.encode('ascii'))[16:]

    aes = AES.new(binascii.unhexlify(hex_key), AES.MODE_CBC, iv)
    temp = aes.decrypt(cipher)
    try:
        padding = temp[-1]
        data_temp = temp[:-padding]
    except TypeError:
        padding = ord(temp[-1])
        data_temp = temp[:-padding]

    return data_temp


# Takes a file and a list of passphrases
def decryptLCPbook(inpath, passphrases, parent_object):
    file = ZipFile(open(inpath, 'rb'))

    license = json.loads(file.read('license.lcpl'))
    print("LCP: Found LCP-encrypted book {0}".format(license["id"]))

    # Check algorithm:
    if license["encryption"]["profile"] == "http://readium.org/lcp/basic-profile":
        print("LCP: Book is using lcp/basic-profile encryption.")
        transform_algo = LCPTransform.secret_transform_basic
    elif license["encryption"]["profile"] == "http://readium.org/lcp/profile-1.0":
        print("LCP: Book is using lcp/profile-1.0 encryption")
        transform_algo = LCPTransform.secret_transform_profile10
    else:
        file.close()
        raise LCPError("Book is using an unknown LCP encryption standard: {0}".format(license["encryption"]["profile"]))

    if (
            "algorithm" in license["encryption"]["content_key"] and
            license["encryption"]["content_key"]["algorithm"] != "http://www.w3.org/2001/04/xmlenc#aes256-cbc"
    ):
        file.close()
        raise LCPError("Book is using an unknown LCP encryption algorithm: {0}".format(
            license["encryption"]["content_key"]["algorithm"]))

    key_check = license["encryption"]["user_key"]["key_check"]
    encrypted_content_key = license["encryption"]["content_key"]["encrypted_value"]

    # Prepare a list of encryption keys to test:
    password_hashes = []

    # Some providers hard-code the passphrase in the LCPL file. That doesn't happen often,
    # but when it does, these files can be decrypted without knowing any passphrase.

    if "value" in license["encryption"]["user_key"]:
        try:
            password_hashes.append(
                binascii.hexlify(base64.decodebytes(license["encryption"]["user_key"]["value"].encode())).decode(
                    "ascii"))
        except AttributeError:
            # Python 2
            password_hashes.append(
                binascii.hexlify(base64.decodestring(license["encryption"]["user_key"]["value"].encode())).decode(
                    "ascii"))
    if "hex_value" in license["encryption"]["user_key"]:
        password_hashes.append(
            binascii.hexlify(bytearray.fromhex(license["encryption"]["user_key"]["hex_value"])).decode("ascii"))

    # Hash all the passwords provided by the user:
    for possible_passphrase in passphrases:
        algo = "http://www.w3.org/2001/04/xmlenc#sha256"
        if "algorithm" in license["encryption"]["user_key"]:
            algo = license["encryption"]["user_key"]["algorithm"]

        algo, tmp_pw = LCPTransform.userpass_to_hash(possible_passphrase.encode('utf-8'), algo)
        if tmp_pw is not None:
            password_hashes.append(tmp_pw)

    # For all the password hashes, check if one of them decrypts the book:
    correct_password_hash = None

    for possible_hash in password_hashes:
        transformed_hash = transform_algo(possible_hash)
        try:
            decrypted = None
            decrypted = dataDecryptLCP(key_check, transformed_hash)
        except:
            pass

        if (decrypted is not None and decrypted.decode("ascii", errors="ignore") == license["id"]):
            # Found correct password hash, hooray!
            correct_password_hash = transformed_hash
            break

    # Print an error message if none of the passwords worked
    if (correct_password_hash is None):
        print("LCP: Tried {0} passphrases, but none of them could decrypt the book ...".format(len(password_hashes)))

        # Print password hint, if available
        if ("text_hint" in license["encryption"]["user_key"] and license["encryption"]["user_key"]["text_hint"] != ""):
            print("LCP: The book distributor has given you the following passphrase hint: \"{0}\"".format(
                license["encryption"]["user_key"]["text_hint"]))

        print("LCP: Enter the correct passphrase in the DeDRM plugin settings, then try again.")

        # Print password reset instructions, if available
        for link in license["links"]:
            if ("rel" in link and link["rel"] == "hint"):
                print("LCP: You may be able to find or reset your LCP passphrase on the following webpage: {0}".format(
                    link["href"]))
                break

        file.close()
        raise LCPError("No correct passphrase found")

    print("LCP: Found correct passphrase, decrypting book ...")

    # Take the key we found and decrypt the content key:
    decrypted_content_key = dataDecryptLCP(encrypted_content_key, correct_password_hash)

    if decrypted_content_key is None:
        raise LCPError("Decrypted content key is None")

    # Begin decrypting
    decryptor = Decryptor(decrypted_content_key)

    strippedPath = inpath.split("/")
    strippedFile = strippedPath[len(strippedPath)-1].split(".")[0]
    outputFolder = inpath[:-len(strippedPath[len(strippedPath)-1])] + strippedFile

    if not(os.path.exists(outputFolder)) or not(os.path.isdir(outputFolder)):
        os.mkdir(outputFolder)

    manifest = json.loads(file.read('manifest.json'))
    hrefs = [entry["href"] for entry in manifest["readingOrder"]]

    for chapter in hrefs:
        pdfdata = file.read(chapter)
        outputname = outputFolder + "/" + chapter

        with open(outputname, 'wb') as f:
            f.write(decryptor.decrypt(pdfdata))

        print("LCP: Chapter successfully decrypted, exporting to {0}".format(outputname))

    for zipped in file.namelist():
        if zipped.endswith(".png") or zipped.endswith(".jpg") or zipped.endswith(".jpeg"):
            shutil.move(file.extract(zipped), outputFolder + "/" + zipped)
            print("Cover art successfully copied to output folder")

    file.close()


    #from pydub import AudioSegment
    #counter = 0
    #for file in os.listdir(outputFolder):
    #    if file.endswith(".mp3") or file.endswith(".MP3"):
    #        if counter < 4:
    #            if 'combined' in locals():
    #                combined = AudioSegment.from_file(outputFolder + "/" + file, format="mp3") + combined
    #            else:
    #                combined = AudioSegment.from_file(outputFolder + "/" + file, format="mp3")
    #            counter += 1
    #combined.export(outputFolder + "/onefile.mp3", format="mp3")

    return 0


if __name__ == '__main__':
    Run().start()
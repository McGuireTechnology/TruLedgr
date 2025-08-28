//
//  Item.swift
//  TruLedgr
//
//  Created by Nathan McGuire on 8/13/25.
//

import Foundation
import SwiftData

@Model
final class Item {
    var timestamp: Date
    
    init(timestamp: Date) {
        self.timestamp = timestamp
    }
}
